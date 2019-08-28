import json
import boto3
import web3
from signer.config import PREFIX_FREE_CALL, GET_FREE_CALLS_METERING_ARN, NETWORKS
from config import config
from eth_account.messages import defunct_hash_message
from sdk.service_client import ServiceClient
from web3 import Web3
from common.utils import Utils


class Signer:
    def __init__(self, obj_repo, net_id):
        self.repo = obj_repo
        self.net_id = net_id
        self.lambda_client = boto3.client('lambda')
        self.obj_utils = Utils()

    def _free_calls_allowed(self, username, org_id, service_id):
        """
            Method to check free calls exists for given user or not.
            Call monitoring service to get the details
        """
        try:
            lambda_payload = {"httpMethod": "GET",
                              "queryStringParameters": {"organization_id": org_id, "service_id": service_id,
                                                        "username": username}}

            response = self.lambda_client.invoke(FunctionName=GET_FREE_CALLS_METERING_ARN, InvocationType='RequestResponse',
                                                 Payload=json.dumps(lambda_payload))
            response_body_raw = json.loads(
                response.get('Payload').read())['body']
            response_body = json.loads(response_body_raw)
            free_calls_allowed = response_body["free_calls_allowed"]
            total_calls_made = response_body["total_calls_made"]
            is_free_calls_allowed = True if (
                (free_calls_allowed - total_calls_made) > 0) else False
            return is_free_calls_allowed
        except Exception as e:
            print(repr(e))
            raise e

    def signature_for_free_call(self, user_data, org_id, service_id):
        """
            Method to generate signature for free call.
        """
        try:
            username = user_data['authorizer']['claims']['email']
            if self._free_calls_allowed(username=username, org_id=org_id, service_id=service_id):
                current_block_no = self.obj_utils.get_current_block_no(
                    ws_provider=NETWORKS[self.net_id]['ws_provider'])
                provider = Web3.HTTPProvider(
                    NETWORKS[self.net_id]['http_provider'])
                w3 = Web3(provider)
                message = web3.Web3.soliditySha3(["string", "string", "string", "string", "uint256"],
                                                 [PREFIX_FREE_CALL, username, org_id, service_id, current_block_no])
                if not config['private_key'].startswith("0x"):
                    config['private_key'] = "0x" + config['private_key']
                signature = bytes(w3.eth.account.signHash(
                    defunct_hash_message(message), config['private_key']).signature)
                signature = signature.hex()
                if not signature.startswith("0x"):
                    signature = "0x" + signature
                return {"snet-free-call-user-id": username, "snet-payment-channel-signature-bin": signature,
                        "snet-current-block-number": current_block_no, "snet-payment-type": "free-call"}
            else:
                raise Exception(
                    "Free calls expired for username %s.", username)
        except Exception as e:
            print(repr(e))
            raise e

    def _get_user_address(self, username):
        try:
            wallet_address_data = self.repo.execute("SELECT address FROM wallet WHERE username = %s AND status = 1 "
                                                    "LIMIT 1", [username])
            if len(wallet_address_data) == 1:
                return wallet_address_data[0]['address']
            raise Exception(
                "Unable to find wallet address for username %s", username)
        except Exception as e:
            print(repr(e))
            raise e

    def _get_service_metadata(self, org_id, service_id):
        """
            Method to get group details for given org_id and service_id.
        """
        try:
            result = self.repo.execute(
                "SELECT O.*, G.* FROM org_group O, service_group G WHERE O.org_id = G.org_id AND G.group_id = "
                "O.group_id AND G.service_id = %s AND G.org_id = %s AND G.service_row_id IN (SELECT row_id FROM service "
                "WHERE is_curated = 1 ) LIMIT 1", [org_id, service_id])
            if len(result) == 1:
                metadata = result[0]
                payment = json.loads(metadata["payment"])
                pricing = json.loads(metadata["pricing"])
                metadata.update(payment)
                metadata["pricing"] = pricing
                return metadata
            else:
                raise Exception(
                    "Unable to find service for service_id %s", service_id)
        except Exception as e:
            print(repr(e))
            raise e

    def _get_channel_id(self, sender_address, recipient_address, group_id, signer_address):
        """
            Method to fetch channel id from mpe_channel(RDS).
        """
        try:
            channel_data = self.repo.execute(
                "SELECT channel_id FROM mpe_channel WHERE sender = %s AND recipient = %s AND "
                " groupId = %s AND signer = %s LIMIT 1", [sender_address, recipient_address,
                                                          group_id, signer_address])
            if len(channel_data) == 1:
                return channel_data[0]["channel_id"]
            raise Exception("Unable to find channels.")
        except Exception as e:
            print(repr(e))
            raise e

    def signature_for_regular_call(self, user_data, org_id, service_id):
        """
            Method to generate signature for regular call.
        """
        try:
            username = user_data['authorizer']['claims']['email']
            user_address = self._get_user_address(username=username)
            metadata = self._get_service_metadata(
                org_id=org_id, service_id=service_id)
            recipient_address = metadata['payment']['payment_address']
            channel_id = self._get_channel_id(sender_address=user_address, recipient_address=recipient_address,
                                              group_id=metadata['group_id'], signer_address=config["signer_address"])
            object_service_client = ServiceClient(
                config=config, metadata=metadata, options=dict())
            return object_service_client.get_service_call_metadata(channel_id=channel_id)
        except Exception as e:
            print(repr(e))
            raise Exception(
                "Unable to sign regular call for username %s", username)
