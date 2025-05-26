import json
from urllib.parse import urlparse

import boto3
import grpc
import web3
from eth_account.messages import encode_defunct
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.utils import Utils
from common.constant import ProviderType
from resources.certificates.root_certificate import certificate
from signer.settings import settings
from signer.constant import MPE_ADDR_PATH
from signer.stubs import state_service_pb2, state_service_pb2_grpc

logger = get_logger(__name__)

FREE_CALL_EXPIRY=172800

class Signer:
    def __init__(self):
        self.lambda_client = boto3.client("lambda", region_name=settings.aws.REGION_NAME)
        self.obj_utils = Utils()
        self.obj_blockchain_utils = BlockChainUtil(
            provider_type=ProviderType.http.value,
            provider=settings.network.networks[settings.network.id].http_provider,
        )
        self.mpe_address = self.obj_blockchain_utils.read_contract_address(
            net_id=self,
            path=MPE_ADDR_PATH,
            key="address",
            token_name = settings.token_name,
            stage = settings.stage
        )
        self.current_block_no = self.obj_blockchain_utils.get_current_block_no()

    def _get_free_calls_allowed(self, org_id, service_id, group_id):
        lambda_payload = {
            "httpMethod": "GET",
            "pathParameters": {
                "orgId": org_id,
                "serviceId": service_id
            },
        }
        response = self.lambda_client.invoke(
            FunctionName=settings.lambda_arn.get_service_deatails_arn,
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload),
        )
        response_body_raw = json.loads(response.get("Payload").read())["body"]
        get_service_response = json.loads(response_body_raw)
        if get_service_response["status"] == "success":
            groups_data = get_service_response["data"].get("groups", [])
            for group_data in groups_data:
                if group_data["group_id"] == group_id:
                    return group_data["free_calls"]
        raise Exception("Unable to fetch free calls information for service %s under organization %s for %s group.",
                        service_id, org_id, group_id)

    def _get_total_calls_made(self, username, org_id, service_id, group_id):
        lambda_payload = {
            "httpMethod": "GET",
            "queryStringParameters": {
                "organization_id": org_id,
                "service_id": service_id,
                "username": username,
                "group_id": group_id,
            },
        }
        response = self.lambda_client.invoke(
            FunctionName=settings.lambda_arn.metering_arn,
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload),
        )
        if response["StatusCode"] == 200:
            metering_data_raw = json.loads(response.get("Payload").read())["body"]
            total_calls_made = json.loads(metering_data_raw).get("total_calls_made", None)
            if total_calls_made is not None:
                return total_calls_made
        raise Exception("Unable to fetch total calls made for service %s under organization %s for %s group.",
                        service_id, org_id, group_id)

    def _get_no_of_free_call_available(self, username, org_id, service_id, group_id):

        token_to_get_free_call, expiry_date_block, signature, current_block_number, daemon_endpoint,free_calls_allowed = self.token_to_get_free_call(
            username, org_id, service_id, group_id)
        total_free_call_available = 0
        try:

            total_free_call_available = self._get_no_of_free_calls_from_daemon(username, token_to_get_free_call,
                                                                          expiry_date_block, signature,
                                                                          current_block_number, daemon_endpoint)
        except Exception as e:
            logger.info(
                f"Free call from daemon not available switching to metering {org_id} {service_id} {group_id} {username}")
            total_free_call_made = self._get_total_calls_made(username, org_id, service_id, group_id)

            total_free_call_available=free_calls_allowed-total_free_call_made

        return total_free_call_available

    def _free_calls_allowed(self, username, org_id, service_id, group_id):
        """
        Method to check free calls exists for given user or not.
        Call monitoring service to get the details
        """
        free_calls_available = self._get_no_of_free_call_available(username, org_id, service_id, group_id)
        return free_calls_available > 0

    def signature_for_free_call(self, username, org_id, service_id, group_id):
        """
        Method to generate signature for free call.
        """
        try:
            if self._free_calls_allowed(
                username=username, org_id=org_id, service_id=service_id, group_id=group_id):
                current_block_no = self.obj_utils.get_current_block_no(
                    ws_provider=settings.network.networks[settings.network.id].ws_provider
                )
                provider = Web3.HTTPProvider(
                    settings.network.networks[settings.network.id].http_provider
                )
                w3 = Web3(provider)
                message = web3.Web3.solidity_keccak(
                    ["string", "string", "string", "string", "uint256"],
                    [
                        settings.lambda_arn.prefix_free_call,
                        username,
                        org_id,
                        service_id,
                        current_block_no
                    ],
                )
                signer_key = "0x" + settings.signer.KEY if not settings.signer.KEY.startswith("0x") else settings.signer.KEY
                
                signature = bytes(
                    w3.eth.account.sign_message(encode_defunct(message), signer_key).signature
                )

                signature = signature.hex()
                if not signature.startswith("0x"):
                    signature = "0x" + signature
                return {
                    "snet-free-call-user-id": username,
                    "snet-payment-channel-signature-bin": signature,
                    "snet-current-block-number": current_block_no,
                    "snet-payment-type": "free-call",
                    "snet-free-call-auth-token-bin":"",
                    "snet-free-call-token-expiry-block":0
                }
            else:
                raise Exception("Free calls expired for username %s.",
                                username)
        except Exception as e:
            logger.error(repr(e))
            raise e

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
                data_types=data_types, values=values, signer_key=settings.signer.KEY)
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
                data_types=data_types,
                values=values,
                signer_key=settings.signer.KEY
            )
            return {
                "signature": signature,
                "snet-current-block-number": self.current_block_no,
            }
        except Exception as e:
            logger.error(repr(e))
            raise Exception(
                "Unable to generate signature for daemon call for username %s",
                username)

    def signature_for_open_channel_for_third_party(
        self,
        recipient,
        group_id,
        amount_in_cogs,
        expiration,
        message_nonce,
        sender_private_key,
        executor_wallet_address
    ):
        data_types = [
            "string", "address", "address", "address", "address", "bytes32", "uint256", "uint256", "uint256"
        ]
        values = [
            "__openChannelByThirdParty",
            self.mpe_address,
            executor_wallet_address,
            settings.signer.ADDRESS,
            recipient,
            group_id,
            amount_in_cogs,
            expiration,
            message_nonce
        ]
        signature = self.obj_blockchain_utils.generate_signature(data_types=data_types, values=values,
                                                                 signer_key=sender_private_key)
        v, r, s = Web3.to_int(hexstr="0x" + signature[-2:]), signature[:66], "0x" + signature[66:130]
        return {"r": r, "s": s, "v": v, "signature": signature}

    def _get_no_of_free_calls_from_daemon(self, email, token_to_get_free_call, expiry_date_block, signature,
                                          current_block_number, daemon_endpoint):

        request = state_service_pb2.free_CallStateRequest()
        request.user_id = email
        request.token_for_free_call = token_to_get_free_call
        request.token_expiry_date_block = expiry_date_block
        request.signature = signature
        request.current_block = current_block_number

        endpoint_object = urlparse(daemon_endpoint)
        if endpoint_object.port is not None:
            channel_endpoint = endpoint_object.hostname + ":" + str(endpoint_object.port)
        else:
            channel_endpoint = endpoint_object.hostname

        if endpoint_object.scheme == "http":
            channel = grpc.insecure_channel(channel_endpoint)
        elif endpoint_object.scheme == "https":
            channel = grpc.secure_channel(channel_endpoint, grpc.ssl_channel_credentials(root_certificates=certificate))
        else:
            raise ValueError('Unsupported scheme in service metadata ("{}")'.format(endpoint_object.scheme))

        stub = state_service_pb2_grpc.FreeCallStateServiceStub(channel)
        response = stub.GetFreeCallsAvailable(request)

        return response.free_calls_available

    def _is_free_call_available(
        self,
        email,
        token_for_free_call,
        expiry_date_block, signature,
        current_block_number,
        daemon_endpoint
    ):
        free_calls_number = self._get_no_of_free_calls_from_daemon(
            email, token_for_free_call, expiry_date_block, signature, current_block_number, daemon_endpoint
        )

        return free_calls_number > 0
        
    def _get_daemon_endpoint_and_free_call_for_group(self,org_id,service_id,group_id):
        lambda_payload = {
            "httpMethod": "GET",
            "pathParameters": {
                "orgId": org_id,
                "serviceId": service_id
            },
        }
        response = self.lambda_client.invoke(
            FunctionName=settings.lambda_arn.get_service_deatails_arn,
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload),
        )
        response_body_raw = json.loads(response.get("Payload").read())["body"]
        get_service_response = json.loads(response_body_raw)
        if get_service_response["status"] == "success":
            groups_data = get_service_response["data"].get("groups", [])
            for group_data in groups_data:
                if group_data["group_id"] == group_id:
                    return group_data["endpoints"][0]["endpoint"],group_data.get("free_calls",0)
        raise Exception("Unable to fetch daemon Endpoint information for service %s under organization %s for %s group.",
                        service_id, org_id, group_id)

    def token_to_get_free_call(self, email, org_id, service_id, group_id):
        signer_public_key_checksum = Web3.to_checksum_address(settings.signer.ADDRESS)
        current_block_number = self.obj_blockchain_utils.get_current_block_no()
        expiry_date_block = current_block_number + FREE_CALL_EXPIRY
        token_to_get_free_call = self.obj_blockchain_utils.generate_signature_bytes(
            ["string", "address", "uint256"],
            [email, signer_public_key_checksum, expiry_date_block],
            settings.signer.KEY
        )

        signature = self.obj_blockchain_utils.generate_signature_bytes(
            ["string", "string", "string", "string", "string", "uint256", "bytes32"],
            ["__prefix_free_trial", email, org_id, service_id, group_id, current_block_number, token_to_get_free_call],
            settings.signer.KEY
        )

        daemon_endpoint ,free_calls_allowed = self._get_daemon_endpoint_and_free_call_for_group(org_id, service_id, group_id)
        logger.info(f"Got daemon endpoint {daemon_endpoint} for org {org_id} service {service_id} group {group_id}")

        return token_to_get_free_call, expiry_date_block, signature, current_block_number, daemon_endpoint,free_calls_allowed

    def token_to_make_free_call(self, email, org_id, service_id, group_id, user_public_key):
        token_to_get_free_call, expiry_date_block, signature, current_block_number, daemon_endpoint,free_calls_allowed = self.token_to_get_free_call(
            email, org_id, service_id, group_id)

        token_with_expiry_to_make_free_call=""
        if self._is_free_call_available(email, token_to_get_free_call, expiry_date_block, signature,
                                        current_block_number, daemon_endpoint):
            token_with_expiry_to_make_free_call = self.obj_blockchain_utils.generate_signature_bytes(
                ["string", "address", "uint256"],
                [email, Web3.to_checksum_address(user_public_key),
                 expiry_date_block],
                settings.signer.KEY)
        else:
            raise Exception("Free call is not available")

        return {"token_to_make_free_call": token_with_expiry_to_make_free_call.hex(),
                "token_expiration_block": expiry_date_block}
