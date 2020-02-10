from enum import Enum

from upload_utility.config import ORG_BUCKET


class UploadType(Enum):
    ORG_ASSETS = "ORG_ASSETS"
    SERVICE_ASSETS = "SERVICE_ASSETS"
    SERVICE_PAGE_COMPONENTS = "SERVICE_PAGE_COMPONENTS"
    SERVICE_GALLERY_IMAGES = "GALLERY_IMAGES"
    SERVICE_PROTO_FILES = "PROTO_FILES"


UPLOAD_TYPE_DETAILS = {
    UploadType.ORG_ASSETS.value: {
        "required_query_params": ["org_uuid"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_ASSETS.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/services/{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_COMPONENTS.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/services/{}/component/{}_component.{}",
    },
    UploadType.SERVICE_GALLERY_IMAGES.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/services/{}/assets/{}_gallery_image.{}",
    },
    UploadType.SERVICE_PROTO_FILES.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/services/{}/assets/{}_proto_files.{}",
    }
}

ALLOWED_CONTENT_TYPE = ["application/zip", "image/jpg"]
FILE_EXTENSION = {"application/zip": 'zip', "image/jpg": "jpg"}
TEMP_FILE_DIR = "/tmp"
