import tempfile
from enum import Enum

from registry.settings import settings

class FileType(Enum):
    ORG_ASSETS = {
        "file_type": "ORG_ASSETS",
        "required_query_params": ["org_uuid"],
        "bucket": settings.aws.S3.UPLOAD_BUCKET.ORG_BUCKET,
        "bucket_path": "{org_uuid}/assets",
    }
    SERVICE_ASSETS = {
        "file_type": "SERVICE_ASSETS",
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.UPLOAD_BUCKET.ORG_BUCKET,
        "bucket_path": "{org_uuid}/services/{service_uuid}/assets"
    }
    SERVICE_PAGE_COMPONENTS = {
        "file_type": "SERVICE_PAGE_COMPONENTS",
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.UPLOAD_BUCKET.ORG_BUCKET,
        "bucket_path": "{org_uuid}/services/{service_uuid}/component",
    }
    SERVICE_GALLERY_IMAGES = {
        "file_type": "SERVICE_GALLERY_IMAGES",
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.UPLOAD_BUCKET.ORG_BUCKET,
        "bucket_path": "{org_uuid}/services/{service_uuid}/assets",
    }
    SERVICE_PROTO_FILES = {
        "file_type": "SERVICE_PROTO_FILES",
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.UPLOAD_BUCKET.ORG_BUCKET,
        "bucket_path": "{org_uuid}/services/{service_uuid}/proto",
    }


TEMP_FILE_DIR = tempfile.gettempdir()
