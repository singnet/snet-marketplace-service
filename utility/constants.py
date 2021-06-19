import tempfile
from enum import Enum

from utility.config import UPLOAD_BUCKET


class UploadType(Enum):
    FEEDBACK = "FEEDBACK"
    ORG_ASSETS = "ORG_ASSETS"
    SERVICE_ASSETS = "SERVICE_ASSETS"
    SERVICE_PAGE_COMPONENTS = "SERVICE_PAGE_COMPONENTS"
    SERVICE_GALLERY_IMAGES = "SERVICE_GALLERY_IMAGES"
    SERVICE_PROTO_FILES = "SERVICE_PROTO_FILES"


UPLOAD_TYPE_DETAILS = {
    UploadType.FEEDBACK.value: {
        "required_query_params": [],
        "bucket": UPLOAD_BUCKET["FEEDBACK_BUCKET"],
        "bucket_path": "{}_feedback.{}",
    },
    UploadType.ORG_ASSETS.value: {
        "required_query_params": ["org_uuid"],
        "bucket": UPLOAD_BUCKET["ORG_BUCKET"],
        "bucket_path": "{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_ASSETS.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": UPLOAD_BUCKET["ORG_BUCKET"],
        "bucket_path": "{}/services/{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_PAGE_COMPONENTS.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": UPLOAD_BUCKET["ORG_BUCKET"],
        "bucket_path": "{}/services/{}/component/{}_component.{}",
    },
    UploadType.SERVICE_GALLERY_IMAGES.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": UPLOAD_BUCKET["ORG_BUCKET"],
        "bucket_path": "{}/services/{}/assets/{}_gallery_image.{}",
    },
    UploadType.SERVICE_PROTO_FILES.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": UPLOAD_BUCKET["ORG_BUCKET"],
        "bucket_path": "{}/services/{}/proto/{}_proto_files.{}",
    }
}

TEMP_FILE_DIR = tempfile.gettempdir()


class ProtoCompilationRegex(Enum):
    ASSET_URL = "(s3:\/\/ropsten-marketplace-service-assets\/)[a-zA-Z0-9]*(\/services\/)[a-zA-Z0-9_]*(\/proto\/)[^\/.]*(_proto_files.zip)"
    COMPONENT_URL = "(s3:\/\/ropsten-service-components\/assets\/)[a-zA-Z0-9]*(\/)[a-zA-Z0-9_]*(\/proto.tar.gz)"
