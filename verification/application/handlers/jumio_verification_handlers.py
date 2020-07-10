from aws_xray_sdk.core import patch_all

from common.constant import ResponseStatus, StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response
from verification.application.services.verification_manager import VerificationManager
from verification.exceptions import BadRequestException

patch_all()
logger = get_logger(__name__)


def submit(event, context):
    logger.info(f"received submit from jumio {event}")
    query_parameters = event["queryStringParameters"]
    path_parameters = event["pathParameters"]
    if "transactionStatus" not in query_parameters:
        raise BadRequestException()
    status = query_parameters["transactionStatus"]
    verification_id = path_parameters["verification_id"]
    redirect_url = VerificationManager().submit(verification_id, status)
    return generate_lambda_response(StatusCode.FOUND, {"status": ResponseStatus.SUCCESS, "data": {}, "error": {}},
                                    cors_enabled=True, headers={"location": redirect_url})
