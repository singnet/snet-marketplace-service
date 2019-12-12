from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, generate_lambda_response, validate_dict
from common.constant import StatusCode, ResponseStatus
from contract_api.config import NETWORK_ID, SLACK_HOOK
from aws_xray_sdk.core import patch_all
from orchestrator.services.verification_service import VerificationService
from common.exceptions import BadRequestException

patch_all()
logger = get_logger(__name__)

Service = VerificationService()


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def get_fields_handler(event, context):
    required_keys = ["configurationName", "countryCode"]
    if not validate_dict(event["pathParameters"], required_keys):
        raise BadRequestException()
    configuration_name = event["pathParameters"]["configurationName"]
    country_code = event["pathParameters"]["countryCode"]
    response = Service.get_fields(configuration_name, country_code)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})
