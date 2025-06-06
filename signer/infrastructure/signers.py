from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.constant import ProviderType
from signer.settings import settings
from signer.constant import MPE_ADDR_PATH

logger = get_logger(__name__)


class Signer:
    def __init__(self):
        self.obj_blockchain_utils = BlockChainUtil(
            provider_type=ProviderType.http.value,
            provider=settings.network.networks[settings.network.id].http_provider,
        )
        self.mpe_address = self.obj_blockchain_utils.read_contract_address(
            net_id=settings.network.id,
            path=MPE_ADDR_PATH,
            key="address",
            token_name=settings.token_name,
            stage=settings.stage,
        )
        self.current_block_no = self.obj_blockchain_utils.get_current_block_no()

    def generate_signature_to_get_free_call_token(
        self,
        address: str,
        username: str,
        organization_id: str,
        service_id: str,
        group_id: str,
        current_block: int,
    ):
        signature = self.obj_blockchain_utils.generate_signature_bytes(
            ["string", "string", "string", "string", "string", "string", "uint256"],
            [
                "__prefix_free_trial",
                address,
                username,
                organization_id,
                service_id,
                group_id,
                current_block,
            ],
            settings.signer.key,
        )

        return signature

    def generate_signature_for_free_call(
        self,
        address: str,
        username: str,
        organization_id: str,
        service_id: str,
        group_id: str,
        current_block: int,
        token: bytes,
    ):
        signature = self.obj_blockchain_utils.generate_signature_bytes(
            ["string", "string", "string", "string", "string", "string", "uint256", "bytes32"],
            [
                "__prefix_free_trial",
                address,
                username,
                organization_id,
                service_id,
                group_id,
                current_block,
                token,
            ],
            settings.signer.key,
        )

        return signature

    def signature_for_regular_call(self, username, channel_id, nonce, amount):
        """
        Method to generate signature for regular call.
        """
        try:
            data_types = ["string", "address", "uint256", "uint256", "uint256"]
            values = [
                "__MPE_claim_message",
                self.mpe_address,
                channel_id,
                nonce,
                amount,
            ]
            signature = self.obj_blockchain_utils.generate_signature(
                data_types=data_types, values=values, signer_key=settings.signer.key
            )
            return {
                "snet-payment-channel-signature-bin": signature,
                "snet-payment-type": "escrow",
                "snet-payment-channel-id": channel_id,
                "snet-payment-channel-nonce": nonce,
                "snet-payment-channel-amount": amount,
                "snet-current-block-number": self.current_block_no,
            }
        except Exception as e:
            logger.error(repr(e))
            raise Exception("Unable to generate signature for daemon call for username")

    def signature_for_state_service(self, username, channel_id):
        """
        Method to generate signature for state service.
        """
        try:
            data_types = ["string", "address", "uint256", "uint256"]
            values = [
                "__get_channel_state",
                self.mpe_address,
                channel_id,
                self.current_block_no,
            ]
            signature = self.obj_blockchain_utils.generate_signature(
                data_types=data_types, values=values, signer_key=settings.signer.key
            )
            return {
                "signature": signature,
                "snet-current-block-number": self.current_block_no,
            }
        except Exception as e:
            logger.error(repr(e))
            raise Exception(
                "Unable to generate signature for daemon call for username %s", username
            )

    def signature_for_open_channel_for_third_party(
        self,
        recipient,
        group_id,
        amount_in_cogs,
        expiration,
        message_nonce,
        sender_private_key,
        executor_wallet_address,
    ):
        data_types = [
            "string",
            "address",
            "address",
            "address",
            "address",
            "bytes32",
            "uint256",
            "uint256",
            "uint256",
        ]
        values = [
            "__openChannelByThirdParty",
            self.mpe_address,
            executor_wallet_address,
            settings.signer.address,
            recipient,
            group_id,
            amount_in_cogs,
            expiration,
            message_nonce,
        ]
        signature = self.obj_blockchain_utils.generate_signature(
            data_types=data_types, values=values, signer_key=sender_private_key
        )
        v, r, s = (
            Web3.to_int(hexstr="0x" + signature[-2:]),
            signature[:66],
            "0x" + signature[66:130],
        )
        return {"r": r, "s": s, "v": v, "signature": signature}
