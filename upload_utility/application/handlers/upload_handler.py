import base64
from uuid import uuid4

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from upload_utility.application.upload_service import UploadService
from upload_utility.config import SLACK_HOOK, NETWORK_ID
from upload_utility.constants import UPLOAD_TYPE_DETAILS, ALLOWED_CONTENT_TYPE, FILE_EXTENSION, TEMP_FILE_DIR
from upload_utility.exceptions import EXCEPTIONS, InvalidContentType, BadRequestException

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def upload_file(event, context):
    content_type = event["header"]["Content-Type"]
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_string_parameter = event["queryStringParameters"]

    if content_type not in ALLOWED_CONTENT_TYPE or len(event["body"]) == 0:
        InvalidContentType()

    upload_request_type = query_string_parameter["type"]
    if upload_request_type not in UPLOAD_TYPE_DETAILS:
        BadRequestException()

    query_string_parameter.pop("type")
    if not validate_dict(query_string_parameter, UPLOAD_TYPE_DETAILS[upload_request_type]):
        BadRequestException()

    file_extension = FILE_EXTENSION[content_type]
    temp_file_path = f"{TEMP_FILE_DIR}/{uuid4().hex}_upload.{file_extension}"
    raw_file_data = base64.b64decode(event["body"])
    with open(temp_file_path, 'wb') as file:
        file.write(raw_file_data)

    response = UploadService().store_file(
        upload_request_type, {"file_path": temp_file_path, "file_extension": file_extension},
        query_string_parameter, username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": {"url": response}, "error": {}}, cors_enabled=True
    )
