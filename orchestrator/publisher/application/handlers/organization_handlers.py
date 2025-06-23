import json

from common.constant import StatusCode, ResponseStatus
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import validate_dict, generate_lambda_response
from orchestrator.config import SLACK_HOOK, NETWORK_ID
from orchestrator.publisher.application.services.organization_service import OrganizationOrchestratorService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def register_org_member(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    required_keys = ["wallet_address", "invite_code"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = OrganizationOrchestratorService().register_org_member(username, payload)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": ResponseStatus.SUCCESS, "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def create_org(event, context):
    payload = json.loads(event["body"])
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    response = OrganizationOrchestratorService().create_and_initiate_verification(payload, username)
    return generate_lambda_response(StatusCode.CREATED,
                                    {"status": ResponseStatus.SUCCESS, "data": response, "error": {}},
                                    cors_enabled=True)
