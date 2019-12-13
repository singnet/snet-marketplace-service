import json
from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, generate_lambda_response, validate_dict
from common.constant import StatusCode, ResponseStatus
from orchestrator.config import NETWORK_ID, SLACK_HOOK
from aws_xray_sdk.core import patch_all
from orchestrator.services.verification_service import VerificationService
from common.exceptions import BadRequestException

patch_all()
logger = get_logger(__name__)

verification_service = VerificationService()


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def get_verification_fields(event, context):
    required_keys = ["configurationName", "countryCode"]
    if not validate_dict(event["pathParameters"], required_keys):
        raise BadRequestException()
    configuration_name = event["pathParameters"]["configurationName"]
    country_code = event["pathParameters"]["countryCode"]
    response = verification_service.get_fields(
        configuration_name, country_code)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def get_document_types_handler(event, context):
    required_keys = ["countryCode"]
    if not validate_dict(event["pathParameters"], required_keys):
        raise BadRequestException()
    country_code = event["pathParameters"]["countryCode"]
    response = verification_service.get_document_types(country_code)


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def get_verification_transaction_data(event, context):
    payload = json.dumps(event["body"])
    response = verification_service.get_verification_transaction(
        payload=payload)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})
