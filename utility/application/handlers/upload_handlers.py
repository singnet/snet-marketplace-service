import base64
import os
from uuid import uuid4

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from utility.application.upload_service import UploadService
from utility.config import ALLOWED_CONTENT_TYPE, FILE_EXTENSION
from utility.constants import UPLOAD_TYPE_DETAILS, TEMP_FILE_DIR
from utility.exceptions import EXCEPTIONS, InvalidContentType, BadRequestException

logger = get_logger(__name__)


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def upload_file(event, context):
    logger.debug(f"Received event: {event}")

    headers = event["headers"]

    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_string_parameter = event["queryStringParameters"]

    content_type = get_content_type(headers)
    if len(event["body"]) == 0:
        logger.error(f"empty file for content_type: {content_type} query_params: {query_string_parameter}")
        raise BadRequestException()

    is_valid_upload_type, upload_request_type = get_and_validate_upload_type(query_string_parameter)
    if not is_valid_upload_type:
        logger.error(f"Failed to get required query params content_type: {content_type} "
                     f"upload_type: {upload_request_type} params: {query_string_parameter}")
        raise BadRequestException()

    file_extension = FILE_EXTENSION[content_type]
    temp_file_path = os.path.join(TEMP_FILE_DIR, f"{uuid4().hex}_upload.{file_extension}")
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


def get_content_type(headers):
    modified_headers = {}
    for key in headers:
        modified_headers[key.lower()] = headers[key]
    if "content-type" not in modified_headers:
        raise InvalidContentType()
    else:
        content_type = modified_headers["content-type"]

    if content_type not in ALLOWED_CONTENT_TYPE:
        logger.error(f"Invalid Content type {content_type}")
        raise InvalidContentType()
    return content_type


def get_and_validate_upload_type(query_string_parameter):
    upload_request_type = "NOT_GIVEN"
    if "type" in query_string_parameter and query_string_parameter["type"] in UPLOAD_TYPE_DETAILS:
        upload_request_type = query_string_parameter["type"]
        query_string_parameter.pop("type")
        if validate_dict(query_string_parameter, UPLOAD_TYPE_DETAILS[upload_request_type]["required_query_params"]):
            return True, upload_request_type
    return False, upload_request_type
