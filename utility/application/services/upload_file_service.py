import os
from uuid import uuid4

from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import date_time_for_filename
from utility.application.schemas import UploadFileRequest
from utility.settings import settings
from utility.constants import UPLOAD_TYPE_DETAILS, UploadType, TEMP_FILE_DIR

logger = get_logger(__name__)


class UploadService:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name=settings.aws.REGION_NAME)

    def store_file(self, request: UploadFileRequest) -> dict[str, str]:

        upload_type = request.type
        content_type = request.content_type
        raw_file_data = request.raw_file_data
        file_extension = settings.files.FILE_EXTENSION[content_type]
        temp_file_path = os.path.join(TEMP_FILE_DIR, f"{uuid4().hex}_upload.{file_extension}")
        org_uuid = request.org_uuid
        service_uuid = request.service_uuid

        with open(temp_file_path, 'wb') as file:
            file.write(raw_file_data)

        bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
        bucket_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"]
        bucket_path_params = [date_time_for_filename(), file_extension]
        if upload_type == UploadType.FEEDBACK.value:
            pass
        elif upload_type == UploadType.ORG_ASSETS.value:
            bucket_path_params = [service_uuid] + bucket_path_params
        else:
            bucket_path_params = [org_uuid, service_uuid] + bucket_path_params

        dest_file_path = bucket_path.format(*bucket_path_params)

        self.boto_utils.s3_upload_file(temp_file_path, bucket, dest_file_path)
        file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
        return {"url": file_url}
