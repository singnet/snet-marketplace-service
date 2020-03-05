import json

from common.constant import StatusCode
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import validate_dict, generate_lambda_response, handle_exception_with_slack_notification
from orchestrator.config import SLACK_HOOK, NETWORK_ID
from orchestrator.publisher.application.services.organization_service import OrganizationOrchestratorService

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def register_org_member(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    required_keys = ["wallet_address", "invite_code"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = OrganizationOrchestratorService().register_org_member(username, payload)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
