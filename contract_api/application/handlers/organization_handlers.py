from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from contract_api.application.schemas.organization_schemas import GetGroupRequest
from contract_api.application.services.organization_service import OrganizationService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_all_organizations(event, context):
    response = OrganizationService().get_all_organizations()

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled = True
    )


@exception_handler(logger=logger)
def get_group(event, context):
    request = GetGroupRequest.validate_event(event)

    response = OrganizationService().get_group(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response}, cors_enabled = True
    )
