from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, generate_lambda_response
from contract_api.config import NETWORK_ID, SLACK_HOOK
from aws_xray_sdk.core import patch_all
from orchestrator.services.verification_service import VerificationService

patch_all()
logger = get_logger(__name__)

Service = VerificationService()


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def get_fields(event, context):
    configuration_name = event["pathParameters"]["configurationName"]
    country_code = event["pathParameters"]["countryCode"]
    response = Service.get_fields(configuration_name, country_code)
    return generate_lambda_response(200, {"status": "success", "data": response})
