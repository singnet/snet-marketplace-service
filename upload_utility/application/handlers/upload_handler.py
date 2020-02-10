from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from upload_utility.application.upload_service import UploadService
from upload_utility.config import SLACK_HOOK, NETWORK_ID, ALLOWED_CONTENT_TYPE
from upload_utility.constants import UPLOAD_TYPE
from upload_utility.exceptions import EXCEPTIONS, InvalidContentType, BadRequestException

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def upload_file(event, context):
    content_type = event["header"]["Content-Type"]
    query_string_parameter = event["queryStringParameters"]
    if content_type not in ALLOWED_CONTENT_TYPE:
        InvalidContentType()
    if query_string_parameter["type"] not in UPLOAD_TYPE:
        BadRequestException()

    response = UploadService().validate_and_store_file()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
