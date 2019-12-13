import json

from common.constant import StatusCode
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import validate_dict, handle_exception_with_slack_notification, generate_lambda_response
from registry.config import SLACK_HOOK, NETWORK_ID
from registry.domain.services.organization_service import OrganizationService

logger = get_logger(__name__)


def get_all_org(event, context):
    pass


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def add_org(event, context):
    payload = json.loads(event["body"])
    required_keys = [""]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = OrganizationService().add_organization_draft(payload)
    return generate_lambda_response(
        StatusCode,
        {"status": "success", "message": response, "error": {}}, cors_enabled=True)


def get_org(event, context):
    pass


def get_all_groups_for_org(event, context):
    pass


def add_group_for_org(event, context):
    pass


def get_group_for_org(event, context):
    pass
