import boto3

from common.logger import get_logger
from common.utils import Utils
from registry.application.services.file_service.constants import FileType
from registry.config import SLACK_HOOK
from registry.exceptions import InvalidFileTypeException, FileNotFoundException

logger = get_logger(__name__)


class FileService:

    def delete(self, file_details):
        bucket, prefix = self.get_s3_bucket_and_prefix(file_details)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket)
        s3_delete_response = bucket.objects.filter(Prefix=prefix).delete()
        """
        boto==1.10.9 
        s3_delete_response = [{
            'Deleted': [
                {
                    'Key': 'string'
                },
            ],
            'Errors': [
                {
                    'Key': 'string',
                    'VersionId': 'string',
                    'Code': 'string',
                    'Message': 'string'
                },
            ]
        }]"""
        successful_deletes = []
        unsuccessful_deletes = []
        for s3_response in s3_delete_response:
            successful_deletes.extend(s3_response.get("Deleted", []))
            unsuccessful_deletes.extend(s3_response.get('Errors', []))

        unsuccessful_files = [s3_file_details.get("Key", "") for s3_file_details in unsuccessful_deletes]
        response = {
            "deleted": [s3_file_details.get("Key", "") for s3_file_details in successful_deletes],
            "errors": unsuccessful_files
        }

        if not successful_deletes:
            if not unsuccessful_deletes:
                raise FileNotFoundException()
            raise Exception("Failed to delete files")

        self.send_slack_alert(unsuccessful_files)
        return response

    def send_slack_alert(self, unsuccessful_files):
        slack_msg = f"Failed to delete files\n```{unsuccessful_files}```"
        return Utils().report_slack(slack_msg=slack_msg, SLACK_HOOK=SLACK_HOOK)

    def get_s3_bucket_and_prefix(self, file_details):
        file_type = file_details.get("type", None)
        if file_type is None:
            raise InvalidFileTypeException()

        if file_type == FileType.ORG_ASSETS.value["file_type"] and "org_uuid" in file_details:
            org_uuid = file_details["org_uuid"]
            bucket = FileType.ORG_ASSETS.value["bucket"]
            prefix = FileType.ORG_ASSETS.value["bucket_path"].format(org_uuid=org_uuid)

        elif file_type == FileType.SERVICE_ASSETS.value["file_type"] and "org_uuid" in file_details \
                and "service_uuid" in file_details:
            org_uuid = file_details["org_uuid"]
            service_uuid = file_details["service_uuid"]
            bucket = FileType.SERVICE_ASSETS.value["bucket"]
            prefix = FileType.SERVICE_ASSETS.value["bucket_path"] \
                .format(org_uuid=org_uuid, service_uuid=service_uuid)

        elif file_type == FileType.SERVICE_PROTO_FILES.value["file_type"] and "org_uuid" in file_details \
                and "service_uuid" in file_details:
            org_uuid = file_details["org_uuid"]
            service_uuid = file_details["service_uuid"]
            bucket = FileType.SERVICE_PROTO_FILES.value["bucket"]
            prefix = FileType.SERVICE_PROTO_FILES.value["bucket_path"] \
                .format(org_uuid=org_uuid, service_uuid=service_uuid)

        elif file_type == FileType.SERVICE_PAGE_COMPONENTS.value["file_type"] and "org_uuid" in file_details \
                and "service_uuid" in file_details:
            org_uuid = file_details["org_uuid"]
            service_uuid = file_details["service_uuid"]
            bucket = FileType.SERVICE_PAGE_COMPONENTS.value["bucket"]
            prefix = FileType.SERVICE_PAGE_COMPONENTS.value["bucket_path"] \
                .format(org_uuid=org_uuid, service_uuid=service_uuid)

        elif file_type == FileType.SERVICE_GALLERY_IMAGES.value["file_type"] and "org_uuid" in file_details \
                and "service_uuid" in file_details:
            org_uuid = file_details["org_uuid"]
            service_uuid = file_details["service_uuid"]
            bucket = FileType.SERVICE_GALLERY_IMAGES.value["bucket"]
            prefix = FileType.SERVICE_GALLERY_IMAGES.value["bucket_path"] \
                .format(org_uuid=org_uuid, service_uuid=service_uuid)
        else:
            raise InvalidFileTypeException()

        return bucket, prefix
