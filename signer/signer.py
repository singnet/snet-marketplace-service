import json

import boto3
import web3
from config import config
from eth_account.messages import defunct_hash_message
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from common.utils import Utils
from signer.config import GET_FREE_CALLS_METERING_ARN
from signer.config import NETWORKS
from signer.config import PREFIX_FREE_CALL
from signer.config import REGION_NAME
from signer.config import SIGNER_KEY
from signer.constant import MPE_ADDR_PATH

logger = get_logger(__name__)


class Signer:
    def __init__(self, net_id):
        self.net_id = net_id
        self.lambda_client = boto3.client("lambda", region_name=REGION_NAME)
        self.obj_utils = Utils()
        self.obj_blockchain_utils = BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[self.net_id]["http_provider"],
        )
        self.mpe_address = self.obj_blockchain_utils.read_contract_address(
            net_id=self.net_id, path=MPE_ADDR_PATH, key="address")
        self.current_block_no = self.obj_blockchain_utils.get_current_block_no(
        )

    def _free_calls_allowed(self, username, org_id, service_id):
        """
            Method to check free calls exists for given user or not.
            Call monitoring service to get the details
        """
        try:
            lambda_payload = {
                "httpMethod": "GET",
                "queryStringParameters": {
                    "organization_id": org_id,
                    "service_id": service_id,
                    "username": username,
                },
            }

            response = self.lambda_client.invoke(
                FunctionName=GET_FREE_CALLS_METERING_ARN,
                InvocationType="RequestResponse",
                Payload=json.dumps(lambda_payload),
            )
            response_body_raw = json.loads(
                response.get("Payload").read())["body"]
            response_body = json.loads(response_body_raw)
            free_calls_allowed = response_body["free_calls_allowed"]
            total_calls_made = response_body["total_calls_made"]
            is_free_calls_allowed = (True if (
                (free_calls_allowed - total_calls_made) > 0) else False)
            return is_free_calls_allowed
        except Exception as e:
            logger.error(repr(e))
            raise e

    def signature_for_free_call(self, user_data, org_id, service_id):
        """
            Method to generate signature for free call.
        """
        try:
            username = user_data["authorizer"]["claims"]["email"]
            if self._free_calls_allowed(username=username,
                                        org_id=org_id,
                                        service_id=service_id):
                current_block_no = self.obj_utils.get_current_block_no(
                    ws_provider=NETWORKS[self.net_id]["ws_provider"])
                provider = Web3.HTTPProvider(
                    NETWORKS[self.net_id]["http_provider"])
                w3 = Web3(provider)
                message = web3.Web3.soliditySha3(
                    ["string", "string", "string", "string", "uint256"],
                    [
                        PREFIX_FREE_CALL, username, org_id, service_id,
                        current_block_no
                    ],
                )
                if not config["private_key"].startswith("0x"):
                    config["private_key"] = "0x" + config["private_key"]
                signature = bytes(
                    w3.eth.account.signHash(defunct_hash_message(message),
                                            config["private_key"]).signature)
                signature = signature.hex()
                if not signature.startswith("0x"):
                    signature = "0x" + signature
                return {
                    "snet-free-call-user-id": username,
                    "snet-payment-channel-signature-bin": signature,
                    "snet-current-block-number": current_block_no,
                    "snet-payment-type": "free-call",
                }
            else:
                raise Exception("Free calls expired for username %s.",
                                username)
        except Exception as e:
            logger.error(repr(e))
            raise e

    def signature_for_regular_call(self, user_data, channel_id, nonce, amount):
        """
            Method to generate signature for regular call.
        """
        try:
            username = user_data["authorizer"]["claims"]["email"]
            data_types = ["string", "address", "uint256", "uint256", "uint256"]
            values = [
                "__MPE_claim_message",
                self.mpe_address,
                channel_id,
                nonce,
                amount,
            ]
            signature = self.obj_blockchain_utils.generate_signature(
                data_types=data_types, values=values, signer_key=SIGNER_KEY)
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
            raise Exception(
                "Unable to generate signature for daemon call for username %s",
                username)

    def signature_for_state_service(self, user_data, channel_id):
        """
            Method to generate signature for state service.
        """
        try:
            username = user_data["authorizer"]["claims"]["email"]
            data_types = ["string", "address", "uint256", "uint256"]
            values = [
                "__get_channel_state",
                self.mpe_address,
                channel_id,
                self.current_block_no,
            ]
            signature = self.obj_blockchain_utils.generate_signature(
                data_types=data_types, values=values, signer_key=SIGNER_KEY)
            return {
                "signature": signature,
                "snet-current-block-number": self.current_block_no,
            }
        except Exception as e:
            logger.error(repr(e))
            raise Exception(
                "Unable to generate signature for daemon call for username %s",
                username)
