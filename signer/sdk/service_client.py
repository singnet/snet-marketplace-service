import importlib
import web3
import grpc

from rfc3986 import urlparse
from eth_account.messages import defunct_hash_message
from snet_cli.utils import RESOURCES_PATH, add_to_path, bytes32_to_str
from sdk.mpe_contract import MPEContract
from sdk.account import Account
from sdk.payment_channel import PaymentChannel


class ServiceClient:
    def __init__(self, config, metadata, options):
        self._config = config
        eth_rpc_endpoint = self._config.get("eth_rpc_endpoint", "https://mainnet.infura.io")
        provider = web3.HTTPProvider(eth_rpc_endpoint)
        self.web3 = web3.Web3(provider)
        self.mpe_contract = MPEContract(self.web3)
        self.account = Account(self.web3, self._config, self.mpe_contract)

        self.options = options
        self.metadata = metadata
        self.expiry_threshold = self.metadata["payment_expiration_threshold"]
        self._base_grpc_channel = self._get_grpc_channel()
        self.payment_channel_state_service_client = self._generate_payment_channel_state_service_client()
        self.payment_channels = []
        self.last_read_block = 0

    def _get_grpc_channel(self):
        endpoint = self.options.get("endpoint", None)
        if endpoint is None:
            endpoint = self.metadata["endpoint"]
        endpoint_object = urlparse(endpoint)
        if endpoint_object.port is not None:
            channel_endpoint = endpoint_object.hostname + ":" + str(endpoint_object.port)
        else:
            channel_endpoint = endpoint_object.hostname

        print("Opening grpc to " + channel_endpoint)
        if endpoint_object.scheme == "http":
            return grpc.insecure_channel(channel_endpoint)
        elif endpoint_object.scheme == "https":
            return grpc.secure_channel(channel_endpoint, grpc.ssl_channel_credentials())
        else:
            raise ValueError('Unsupported scheme in service metadata ("{}")'.format(endpoint_object.scheme))

    def get_service_call_metadata(self, channel_id):
        channel = PaymentChannel(channel_id, self.web3, self.account,
                                 self, self.mpe_contract)
        print("Got channel " + str(channel.channel_id) + " " + str(channel.account) + " " + str(channel.state))
        channel.sync_state();
        print("Sync channel " + str(channel.channel_id) + " " + str(channel.account) + " " + str(channel.state))
        amount = channel.state["last_signed_amount"] + int(self.metadata["pricing"]["price_in_cogs"])
        message = web3.Web3.soliditySha3(
            ["address", "uint256", "uint256", "uint256"],
            [self.mpe_contract.contract.address, channel.channel_id, channel.state["nonce"], amount]
        )
        signature = bytes(self.web3.eth.account.signHash(defunct_hash_message(message), self.account.signer_private_key).signature)
        signature = str(signature.hex())
        metadata = {
                    "snet-payment-channel-id": str(channel.channel_id),
                    "snet-payment-channel-nonce": str(channel.state["nonce"]),
                    "snet-payment-channel-amount": str(amount),
                    "snet-payment-channel-signature-bin": signature
                    }
        return metadata

    def update_channel_states(self):
        for channel in self.payment_channels:
            channel.sync_state()
        return self.payment_channels

    def default_channel_expiration(self):
        current_block_number = self.web3.eth.getBlock("latest").number
        return current_block_number + self.expiry_threshold

    def _generate_payment_channel_state_service_client(self):
        grpc_channel = self._base_grpc_channel
        with add_to_path(str(RESOURCES_PATH.joinpath("proto"))):
            state_service_pb2_grpc = importlib.import_module("state_service_pb2_grpc")
        return state_service_pb2_grpc.PaymentChannelStateServiceStub(grpc_channel)