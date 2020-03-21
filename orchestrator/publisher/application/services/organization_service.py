import json

from common.boto_utils import BotoUtils
from common.logger import get_logger
from orchestrator.config import REGION_NAME, REGISTRY_ARN, WALLETS_SERVICE_ARN, VERIFICATION_ARN
from orchestrator.constant import VerificationType, OrganizationType

logger = get_logger(__name__)


class OrganizationOrchestratorService:

    def __init__(self):
        self.boto_client = BotoUtils(REGION_NAME)

    def register_org_member(self, username, payload):
        wallet_address = payload["wallet_address"]
        invite_code = payload["invite_code"]
        self.registry_register_org_member(username, wallet_address, invite_code)
        self.register_wallet(username, wallet_address)
        return "OK"

    def registry_register_org_member(self, username, wallet_address, invite_code):
        register_member_event = {
            "path": f"/org/member/register",
            "body": json.dumps({"wallet_address": wallet_address,
                                "invite_code": invite_code}),
            "httpMethod": "POST",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": username
                    }
                }
            }
        }

        logger.info(f"Requesting register user for invite_code: {invite_code} "
                    f"username: {username} wallet_address:{wallet_address}")

        register_member_response = self.boto_client.invoke_lambda(
            lambda_function_arn=REGISTRY_ARN["REGISTER_MEMBER_ARN"],
            invocation_type='RequestResponse',
            payload=json.dumps(register_member_event)
        )
        if register_member_response["statusCode"] != 201:
            raise Exception(f"Failed to register user for invite_code: {invite_code} "
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

    def create_and_initiate_verification(self, create_org_details, username):
        org_details = self.create_org(create_org_details, username)
        org_uuid = org_details["org_uuid"]
        org_type = org_details["org_type"]
        if org_type == OrganizationType.ORGANIZATION.value:
            self.initiate_verification(org_uuid, VerificationType.DUNS.value, username)
        elif org_type == OrganizationType.INDIVIDUAL.value:
            self.initiate_verification(username, VerificationType.JUMIO.value, username)
        else:
            raise Exception(f"Verification initiate failed for Invalid org type {org_type}")
        return org_details

    def initiate_verification(self, entity_id, verification_type, username):
        if verification_type == VerificationType.JUMIO.value:
            initiate_verification_payload = {
                "requestContext": {"authorizer": {"claims": {"email": entity_id}}},
                "body": json.dumps({
                    "type": verification_type
                })
            }
        elif verification_type == VerificationType.DUNS.value:
            initiate_verification_payload = {
                "requestContext": {"authorizer": {"claims": {"email": username}}},
                "body": json.dumps({
                    "type": verification_type,
                    "entity_id": entity_id
                })
            }
        else:
            raise Exception(f"Verification initiate failed for Invalid verification type {verification_type}")

        raw_response = self.boto_client.invoke_lambda(lambda_function_arn=VERIFICATION_ARN["INITIATE"],
                                                      invocation_type="RequestResponse",
                                                      payload=json.dumps(initiate_verification_payload))
        status = raw_response["statusCode"]
        if status != 201:
            raise Exception("Failed to create Organization")

    def create_org(self, org_details, username):
        create_organization_payload = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "body": json.dumps(org_details)
        }
        raw_response = self.boto_client.invoke_lambda(lambda_function_arn=REGISTRY_ARN["CREATE_ORG_ARN"],
                                                      invocation_type="RequestResponse",
                                                      payload=json.dumps(create_organization_payload))
        status = raw_response["statusCode"]
        if status != 201:
            raise Exception("Failed to create Organization")
        return json.loads(raw_response["body"])
