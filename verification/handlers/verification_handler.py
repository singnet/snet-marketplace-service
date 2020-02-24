from aws_xray_sdk.core import patch_all
from common.constant import StatusCode, ResponseStatus
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, generate_lambda_response, validate_dict
from verification.config import NETWORK_ID, SLACK_HOOK
from verification.services.verification_service import VerificationService

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
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def get_verification_transaction_data(event, context):
    payload = event["body"]
    response = verification_service.get_verification_transaction(
        payload=payload)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})


@handle_exception_with_slack_notification(logger=logger, SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID)
def dummy_for_redirection(event, context):
    return generate_lambda_response(
        StatusCode.FOUND, {},
        headers={"location": "http://ropsten-publisher.singularitynet.io.s3-website-us-east-1.amazonaws.com/enroll",
                 "Referrer-Policy": "unsafe-url"},
        cors_enabled=True)
