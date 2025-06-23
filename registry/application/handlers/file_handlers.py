from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from registry.application.access_control.authorization import secured
from registry.application.services.file_service.file_service import FileService
from registry.constants import Action
from registry.exceptions import EXCEPTIONS, BadRequestException

logger = get_logger(__name__)


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.UPDATE, org_uuid_path=("queryStringParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def delete(event, context):
    query_parameters = event["queryStringParameters"]

    if "type" not in query_parameters:
        raise BadRequestException()
    response = FileService().delete(query_parameters)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
