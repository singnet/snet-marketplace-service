
from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.schemas import PayloadValidationError
from common.utils import generate_lambda_response
from utility.application.schemas import UploadFileRequest
from utility.application.services.upload_file_service import UploadService
from utility.settings import settings
from utility.exceptions import EXCEPTIONS, BadRequestException

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=settings.slack, NETWORK_ID=settings.network.id, logger=logger, EXCEPTIONS=EXCEPTIONS)
def upload_file(event, context):
    try:
        request = UploadFileRequest.validate_event(event)
    except PayloadValidationError:
        raise BadRequestException()

    response = UploadService().store_file(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )
