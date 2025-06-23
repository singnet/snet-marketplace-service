from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from utility.application.schemas import UploadFileRequest
from utility.application.services.upload_file_service import UploadService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def upload_file(event, context):
    request = UploadFileRequest.validate_event(event)

    response = UploadService().store_file(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )