import base64
from uuid import uuid4

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from utility.application.upload_service import UploadService
from utility.config import SLACK_HOOK, NETWORK_ID, ALLOWED_CONTENT_TYPE, FILE_EXTENSION
from utility.constants import UPLOAD_TYPE_DETAILS, TEMP_FILE_DIR
from utility.exceptions import EXCEPTIONS, InvalidContentType, BadRequestException

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def upload_file(event, context):
    headers = event["headers"]
    if "content-type" not in headers:
        if "Content-Type" not in headers:
            logger.error(f"Content type not found content type")
            raise InvalidContentType()
        else:
            content_type = headers["Content-Type"]
    else:
        content_type = headers["content-type"]

    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_string_parameter = event["queryStringParameters"]

    if content_type not in ALLOWED_CONTENT_TYPE:
        logger.error(f"Invalid Content type {content_type}")
        raise InvalidContentType()

    if not ("type" in query_string_parameter and
            query_string_parameter["type"] in UPLOAD_TYPE_DETAILS) or len(event["body"]) == 0:
        logger.error(f"Invalid request for content_type: {content_type} query_params: {query_string_parameter}")
        raise BadRequestException()

    upload_request_type = query_string_parameter["type"]
    query_string_parameter.pop("type")
    if not validate_dict(query_string_parameter, UPLOAD_TYPE_DETAILS[upload_request_type]["required_query_params"]):
        logger.error(f"Failed to get required query params content_type: {content_type} "
                     f"upload_type: {upload_request_type} params: {query_string_parameter}")
        raise BadRequestException()

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
