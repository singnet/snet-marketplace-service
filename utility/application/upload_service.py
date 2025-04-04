from common.boto_utils import BotoUtils
from common.logger import get_logger
from utility.config import REGION_NAME
from utility.constants import UPLOAD_TYPE_DETAILS, UploadType
from utility.exceptions import BadRequestException

from datetime import datetime

logger = get_logger(__name__)


class UploadService:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name=REGION_NAME)

    def store_file(self, upload_type, file_data, request_params, username):
        """
            TODO: persist user history of the storage request
        """
        if upload_type == UploadType.FEEDBACK.value:
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"]\
                .format(datetime.utcnow().strftime("%Y%m%d%H%M%S"), file_data["file_extension"])
            # TODO: change datetime.utcnow().strftime("%Y%m%d%H%M%S") to common.utils.date_time_for_filename() when updating the Python version

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url

        elif upload_type == UploadType.ORG_ASSETS.value:
            org_id = request_params["org_uuid"]
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"].format(
                org_id, datetime.utcnow().strftime("%Y%m%d%H%M%S"), file_data["file_extension"])
            # TODO: change datetime.utcnow().strftime("%Y%m%d%H%M%S") to common.utils.date_time_for_filename() when updating the Python version

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url

        elif upload_type in [UploadType.SERVICE_ASSETS.value, UploadType.SERVICE_GALLERY_IMAGES.value,
                             UploadType.SERVICE_PAGE_COMPONENTS.value, UploadType.SERVICE_PROTO_FILES.value]:
            org_id = request_params["org_uuid"]
            service_id = request_params["service_uuid"]
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"].format(
                org_id, service_id, datetime.utcnow().strftime("%Y%m%d%H%M%S"), file_data["file_extension"])
            # TODO: change datetime.utcnow().strftime("%Y%m%d%H%M%S") to common.utils.date_time_for_filename() when updating the Python version

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url

        else:
            logger.error(f"Invalid upload request type {upload_type} params: {request_params}")
            raise BadRequestException()
