from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from registry.application.services.organization_publisher_service import OrganizationPublisherService
from registry.config import SLACK_HOOK, NETWORK_ID
from registry.exceptions import EXCEPTIONS, BadRequestException

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_all_org(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    response = OrganizationPublisherService(None, username).get_all_org_for_user()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
