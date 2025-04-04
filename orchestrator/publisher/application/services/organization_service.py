import json

from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import send_email_notification, Utils
from orchestrator.config import REGION_NAME, REGISTRY_ARN, VERIFICATION_ARN, NOTIFICATION_ARN, \
    ORG_APPROVERS_DLIST, REGISTER_WALLET_ARN
from orchestrator.constant import VerificationType, OrganizationType
from orchestrator.publisher.mail_templates import get_mail_template_to_user_for_org_onboarding
from orchestrator.publisher.mail_templates import get_org_approval_mail
from registry.config import APPROVAL_SLACK_HOOK

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
            "body": json.dumps(register_wallet_body)
        }
        raw_response = self.boto_client.invoke_lambda(lambda_function_arn=REGISTER_WALLET_ARN,
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
            self.initiate_verification(username, VerificationType.INDIVIDUAL.value, username)
        else:
            raise Exception(f"Verification initiate failed for Invalid org type {org_type}")

        self.notify_approval_team(org_details['org_id'], org_details['org_name'])
        self.notify_user_on_start_of_onboarding_process(org_id=org_details["org_id"], recipients=[username])
        return org_details

    def notify_approval_team(self, org_id, org_name):
        slack_msg = f"Organization with org_id {org_id} is submitted for approval"
        mail_template = get_org_approval_mail(org_id, org_name)
        self.send_slack_message(slack_msg)
        send_email_notification([ORG_APPROVERS_DLIST], mail_template["subject"],
                                mail_template["body"], NOTIFICATION_ARN, self.boto_client)

    def notify_user_on_start_of_onboarding_process(self, org_id, recipients):
        if not recipients:
            logger.info(f"Unable to find recipients for organization with org_id {org_id}")
            return
        mail_template = get_mail_template_to_user_for_org_onboarding(org_id)
        for recipient in recipients:
            send_notification_payload = {"body": json.dumps({
                "message": mail_template["body"],
                "subject": mail_template["subject"],
                "notification_type": "support",
                "recipient": recipient})}
            self.boto_client.invoke_lambda(lambda_function_arn=NOTIFICATION_ARN, invocation_type="RequestResponse",
                                           payload=json.dumps(send_notification_payload))
            logger.info(f"Recipient {recipient} notified for successfully starting onboarding process.")

    def send_slack_message(self, slack_msg):
        Utils().report_slack(slack_msg, APPROVAL_SLACK_HOOK)

    def initiate_verification(self, entity_id, verification_type, username):
        if verification_type == VerificationType.INDIVIDUAL.value:
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
        if status != 200:
            raise Exception("Failed to create Organization")
        return json.loads(raw_response["body"])["data"]
