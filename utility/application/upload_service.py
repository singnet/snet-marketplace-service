from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import date_time_for_filename
from utility.config import REGION_NAME
from utility.constants import UPLOAD_TYPE_DETAILS, UploadType
from utility.exceptions import BadRequestException

logger = get_logger(__name__)


class UploadService:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name=REGION_NAME)

    def store_file(self, upload_type, file_data, request_params):
        """
            TODO: persist user history of the storage request
        """
        if upload_type == UploadType.FEEDBACK.value:
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"] \
                .format(date_time_for_filename(), file_data["file_extension"])

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url, None

        elif upload_type == UploadType.ORG_ASSETS.value:
            org_id = request_params["org_uuid"]
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"].format(
                org_id, date_time_for_filename(), file_data["file_extension"])

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url, None

        elif upload_type in [UploadType.SERVICE_ASSETS.value, UploadType.SERVICE_GALLERY_IMAGES.value,
                             UploadType.SERVICE_PAGE_COMPONENTS.value, UploadType.SERVICE_PROTO_FILES.value]:
            
            if upload_type == UploadType.SERVICE_PROTO_FILES.value:
                training_indicator = self.__aggregate_protos(file_data["file_path"])
            
            org_id = request_params["org_uuid"]
            service_id = request_params["service_uuid"]
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"].format(
                org_id, service_id, date_time_for_filename(), file_data["file_extension"])

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url, training_indicator

        else:
            logger.error(f"Invalid upload request type {upload_type} params: {request_params}")
            raise BadRequestException()
