from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, validate_dict, generate_lambda_response
from common.constant import StatusCode, ResponseStatus
from common.exceptions import BadRequestException
from aws_xray_sdk.core import patch_all
from user_verification.config import SLACK_HOOK, NETWORK_ID
from user_verification.services.user_verification_service import UserVerificationService

patch_all()
logger = get_logger(__name__)

user_verification_service = UserVerificationService()


@handle_exception_with_slack_notification(logger, SLACK_HOOK, NETWORK_ID)
def initiate(event, context):
    required_keys = ["customerInternalReference", "userReference", "successUrl"]
    payload = event["body"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = user_verification_service.initiate(payload)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})


@handle_exception_with_slack_notification(logger, SLACK_HOOK, NETWORK_ID)
def callback(event, context):
    required_keys = ["callBackType", "jumioIdScanReference", "verificationStatus", "idScanStatus", "idScanSource",
                     "idCheckDataPositions", "idCheckDocumentValidation", "idCheckHologram", "idCheckMRZcode",
                     "idCheckMicroprint", "idCheckSecurityFeatures", "idCheckSignature", "transactionDate",
                     "callbackDate"]
    payload = event["body"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = user_verification_service.callback(payload)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})

