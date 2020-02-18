from enum import Enum

from utility.config import ORG_BUCKET


class UploadType(Enum):
    ORG_ASSETS = "ORG_ASSETS"
    SERVICE_ASSETS = "SERVICE_ASSETS"
    SERVICE_PAGE_COMPONENTS = "SERVICE_PAGE_COMPONENTS"
    SERVICE_GALLERY_IMAGES = "SERVICE_GALLERY_IMAGES"
    SERVICE_PROTO_FILES = "SERVICE_PROTO_FILES"


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
    UploadType.SERVICE_PAGE_COMPONENTS.value: {
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
        "bucket_path": "{}/services/{}/proto/{}_proto_files.{}",
    }
}

TEMP_FILE_DIR = "/tmp"
