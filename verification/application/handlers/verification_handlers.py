import json

from common.constant import StatusCode, ResponseStatus
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from verification.application.services.verification_manager import VerificationManager
from verification.config import NETWORK_ID, SLACK_HOOK
from verification.constants import VerificationType
from verification.exceptions import EXCEPTIONS, BadRequestException

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def initiate(event, context):
    payload = json.loads(event["body"])
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    required_keys = ["type"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = VerificationManager().initiate_verification(payload, username)
    return generate_lambda_response(StatusCode.CREATED,
                                    {"status": ResponseStatus.SUCCESS, "data": response, "error": {}},
                                    cors_enabled=True)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def callback(event, context):
    logger.info(f"received event from verification for callback {event}")
    payload = event["body"]
    path_parameters = event["queryStringParameters"]
    if "verification_id" not in path_parameters and "entity_id" not in path_parameters:
        raise BadRequestException()
    entity_id = path_parameters.get("entity_id")
    verification_id = path_parameters.get("verification_id")
    response = VerificationManager().callback(payload, verification_id=verification_id, entity_id=entity_id)
    return generate_lambda_response(StatusCode.CREATED,
                                    {"status": ResponseStatus.SUCCESS, "data": response, "error": {}},
                                    cors_enabled=True)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_status(event, context):
    query_parameters = event["queryStringParameters"]
    if "type" not in query_parameters:
        raise BadRequestException()
    verification_type = query_parameters["type"]
    if verification_type == VerificationType.INDIVIDUAL.value:
        entity_id = event["requestContext"]["authorizer"]["claims"]["email"]
    elif verification_type == VerificationType.DUNS.value:
        entity_id = query_parameters["entity_id"]
    else:
        raise Exception("Invalid verification type")
    response = VerificationManager().get_status_for_entity(entity_id)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response, "error": {}},
                                    cors_enabled=True)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_verifications(event, context):
    query_parameters = event["queryStringParameters"]
    if "type" not in query_parameters:
        raise BadRequestException()
    response = VerificationManager().get_verifications(query_parameters)
    return generate_lambda_response(StatusCode.OK, {"status": ResponseStatus.SUCCESS, "data": response, "error": {}},
                                    cors_enabled=True)
