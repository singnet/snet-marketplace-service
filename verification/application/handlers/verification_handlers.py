import json

from common.constant import StatusCode, ResponseStatus
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from verification.application.services.verification_manager import VerificationManager
from verification.config import NETWORK_ID, SLACK_HOOK
from verification.exceptions import EXCEPTIONS, BadRequestException

logger = get_logger(__name__)


@exception_handler(logger, SLACK_HOOK, NETWORK_ID, EXCEPTIONS)
def initiate(event, context):
    payload = json.loads(event["body"])
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    required_keys = ["type", "entity_id"]
    if not validate_dict(payload, required_keys, strict=True):
        raise BadRequestException()
    response = VerificationManager().initiate_verification(payload, username)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response}, cors_enabled=True)


def callback(event, context):
    pass
