from enum import Enum

from upload_utility.config import ORG_BUCKET


class UploadType(Enum):
    ORG_ASSETS = "ORG_ASSETS"
    SERVICE_ASSETS = "SERVICE_ASSETS"
    SERVICE_COMPONENTS = "SERVICE_COMPONENTS"
    SERVICE_IMAGES = "SERVICE_IMAGES"


UPLOAD_TYPE_DETAILS = {
    UploadType.ORG_ASSETS.value: {
        "required_query_params": ["org_id"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_ASSETS.value: {
        "required_query_params": ["org_id", "service_id"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/services/{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_COMPONENTS.value: {
        "required_query_params": ["org_id", "service_id"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/services/{}/component/{}_component.{}",
    },
    UploadType.SERVICE_IMAGES.value: {
        "required_query_params": ["org_id", "service_id"],
        "bucket": ORG_BUCKET,
        "bucket_path": "{}/services/{}/assets/{}_extra_image.{}",
    }
}

ALLOWED_CONTENT_TYPE = ["application/zip", "image/jpg"]
FILE_EXTENSION = {"application/zip": 'zip', "image/jpg": "jpg"}
TEMP_FILE_DIR = "/tmp"
