from common.boto_utils import BotoUtils
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from common.utils import date_time_for_filename
from utility.config import REGION_NAME, IPFS_URL
from utility.constants import UPLOAD_TYPE_DETAILS, UploadType
from utility.exceptions import BadRequestException

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
                .format(date_time_for_filename(), file_data["file_extension"])

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url

        elif upload_type == UploadType.ORG_ASSETS.value:
            org_id = request_params["org_uuid"]
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"].format(
                org_id, date_time_for_filename(), file_data["file_extension"])

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url

        elif upload_type in [UploadType.SERVICE_ASSETS.value, UploadType.SERVICE_GALLERY_IMAGES.value,
                             UploadType.SERVICE_PAGE_COMPONENTS.value, UploadType.SERVICE_PROTO_FILES.value]:
            org_id = request_params["org_uuid"]
            service_id = request_params["service_uuid"]
            bucket = UPLOAD_TYPE_DETAILS[upload_type]["bucket"]
            dest_file_path = UPLOAD_TYPE_DETAILS[upload_type]["bucket_path"].format(
                org_id, service_id, date_time_for_filename(), file_data["file_extension"])

            self.boto_utils.s3_upload_file(file_data["file_path"], bucket, dest_file_path)

            file_url = f"https://{bucket}.s3.amazonaws.com/{dest_file_path}"
            return file_url

        else:
            logger.error(f"Invalid upload request type {upload_type} params: {request_params}")
            raise BadRequestException()

    def push_asset_to_s3_using_hash(self, hash, s3_filename, s3_bucket_name):
        try:
            io_bytes = IPFSUtil(ipfs_url=IPFS_URL['url'], port=IPFS_URL['port']).read_bytesio_from_ipfs(hash)
            new_url = self.boto_utils.push_io_bytes_to_s3(key=s3_filename, bucket_name=s3_bucket_name, io_bytes=io_bytes)
            return new_url
        except Exception as e:
            logger.info(f" Exception in handling asset for ipfs has :: {hash} ")
            raise e
