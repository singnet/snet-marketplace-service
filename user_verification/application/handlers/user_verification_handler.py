from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, validate_dict, generate_lambda_response
from common.constant import StatusCode, ResponseStatus
from common.exceptions import BadRequestException
from user_verification.config import SLACK_HOOK, NETWORK_ID
from user_verification.application.services.user_verification_service import UserVerificationService
from user_verification.exceptions import BadRequestException
from common.exception_handler import exception_handler

logger = get_logger(__name__)

user_verification_service = UserVerificationService()


@exception_handler(logger, SLACK_HOOK, NETWORK_ID, BadRequestException)
def initiate(event):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    response = user_verification_service.initiate(username)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})

@exception_handler(logger, SLACK_HOOK, NETWORK_ID, BadRequestException)
def submit(event):
    query_params = event["queryStringParameters"]
    transaction_id = query_params.get("customerInternalReference", None)
    jumio_reference = query_params.get("transactionReference", None)
    error_code = query_params.get("errorCode", None)
    response = user_verification_service.submit(transaction_id, jumio_reference, error_code)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})

@exception_handler(logger, SLACK_HOOK, NETWORK_ID, BadRequestException)
def complete(event):
    required_keys = ["callBackType", "jumioIdScanReference", "verificationStatus", "idScanStatus", "idScanSource",
                     "idCheckDataPositions", "idCheckDocumentValidation", "idCheckHologram", "idCheckMRZcode",
                     "idCheckMicroprint", "idCheckSecurityFeatures", "idCheckSignature", "transactionDate",
                     "callbackDate"]
    payload = event["body"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = user_verification_service.complete(payload)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response})

