from aws_xray_sdk.core import patch_all

from common.constant import ResponseStatus, StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response
from verification.application.services.verification_manager import VerificationManager
from verification.exceptions import BadRequestException

patch_all()
logger = get_logger(__name__)


def callback(event, context):
    query_parameters = event["queryStringParameters"]
    payload = event["body"]
    if "entity_id" not in query_parameters:
        raise BadRequestException
    entity_id = query_parameters["entity_id"]
    response = VerificationManager().slack_callback(entity_id, payload)
    return generate_lambda_response(StatusCode.CREATED, {"status": ResponseStatus.SUCCESS, "data": response, "error": {}},
                                    cors_enabled=True)
