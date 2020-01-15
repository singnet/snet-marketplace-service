import json

from common.boto_utils import BotoUtils
from common.logger import get_logger
from orchestrator.config import REGION_NAME, REGISTRY_ARN, WALLETS_SERVICE_ARN

logger = get_logger(__name__)


class OrganizationOrchestratorService:

    def __init__(self):
        self.boto_client = BotoUtils(REGION_NAME)

    def register_org_member(self, username, org_uuid, payload):
        full_name = payload["full_name"]
        phone_number = payload["phone_number"]
        wallet_address = payload["wallet_address"]

        self.dapp_update_user_details(full_name, phone_number)
        self.register_wallet(username, wallet_address)
        self.registry_register_org_member(org_uuid, username, wallet_address)
        return "OK"

    def dapp_update_user_details(self, full_name, phone_number):
        """
        ToDo: Invoke update user lambda
        """
        pass

    def registry_register_org_member(self, org_uuid, username, wallet_address):
        register_member_event = {
            "path": f"/org/{org_uuid}/member/register",
            "pathParameters": {"org_uuid": org_uuid},
            "queryStringParameters": {"wallet_address": wallet_address},
            "httpMethod": "GET",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": username
                    }
                }
            }
        }

        logger.info(f"Requesting register user for org_uuid: {org_uuid} "
                    f"username: {username} wallet_address:{wallet_address}")

        register_member_response = self.boto_client.invoke_lambda(
            lambda_function_arn=REGISTRY_ARN["REGISTER_MEMBER_ARN"],
            invocation_type='RequestResponse',
            payload=json.dumps(register_member_event)
        )
        if register_member_response["statusCode"] != 201:
            raise Exception(f"Failed to register user for org_uuid: {org_uuid} "
                            f"username: {username} wallet_address:{wallet_address}")

    def register_wallet(self, username, wallet_address, wallet_type="METAMASK"):
        register_wallet_body = {
            'address': wallet_address,
            'type': wallet_type,
            'username': username
        }
        register_wallet_payload = {
            "path": "/wallet/register",
            "body": json.dumps(register_wallet_body),
            "httpMethod": "POST"
        }
        raw_response = self.boto_client.invoke_lambda(lambda_function_arn=WALLETS_SERVICE_ARN,
                                                      invocation_type="RequestResponse",
                                                      payload=json.dumps(register_wallet_payload))
        status = raw_response["statusCode"]
        if int(status) != 200:
            raise Exception("Unable to register wallet for username %s", username)
