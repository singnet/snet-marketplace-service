import tempfile
from enum import Enum

from utility.settings import settings


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
        "bucket": settings.aws.S3.FEEDBACK_BUCKET,
        "bucket_path": "{}_feedback.{}",
    },
    UploadType.ORG_ASSETS.value: {
        "required_query_params": ["org_uuid"],
        "bucket": settings.aws.S3.ORG_BUCKET,
        "bucket_path": "{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_ASSETS.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.ORG_BUCKET,
        "bucket_path": "{}/services/{}/assets/{}_asset.{}",
    },
    UploadType.SERVICE_PAGE_COMPONENTS.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.ORG_BUCKET,
        "bucket_path": "{}/services/{}/component/{}_component.{}",
    },
    UploadType.SERVICE_GALLERY_IMAGES.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.ORG_BUCKET,
        "bucket_path": "{}/services/{}/assets/{}_gallery_image.{}",
    },
    UploadType.SERVICE_PROTO_FILES.value: {
        "required_query_params": ["org_uuid", "service_uuid"],
        "bucket": settings.aws.S3.ORG_BUCKET,
        "bucket_path": "{}/services/{}/proto/{}_proto_files.{}",
    }
}

SERVICE_PY_CONTENT = """
from snet import sdk
import config

def main():
    sdk_config = sdk.config.Config(private_key = config.PRIVATE_KEY, 
                               eth_rpc_endpoint = config.ETH_RPC_ENDPOINT)

    snet_sdk = sdk.SnetSDK(sdk_config)
    service_client = snet_sdk.create_service_client(org_id=config.ORG_ID,
                                                    service_id=config.SERVICE_ID)

    arguments = {...} # insert method arguments here
    try:
        response = service_client.call_rpc("<METHOD_NAME>", "<MESSAGE_NAME>", **arguments) # replace METHOD_NAME and MESSAGE_NAME
        print(f"Service invoked successfully :: response :: {response}")
    except Exception as e:
        print(f"Exception when invoking a service :: {e}")


if __name__ == "__main__":
    main()
"""

PYTHON_BOILERPLATE_TEMPLATE = {
    "requirement": {
        "extension": ".txt",
        "content": "snet-sdk"
    },
    "readme": {
        "extension": ".txt",
        "content": "Follow below instructions to setup dependencies :\n" \
                   "1.Create virtual environment\n" \
                   "   Once boilerplate is downloaded cd into the service_id_placeholder-boilerplate folder and execute below commands\n" \
                   "   For unix/macOS:\n" \
                   "      -sudo apt-get install python3-venv\n" \
                   "      -sudo python3 -m venv venv\n" \
                   "      -source ./venv/bin/activate\n" \
                   "   For Windows:\n" \
                   "      -py -m pip install --user virtualenv\n" \
                   "      -py -m venv venv\n" \
                   "      -.\\venv\\Scripts\\activate\n" \
                   "2.Run following command to install dependencies\n" \
                   "   - pip install -r requirement.txt\n" \
                   "3.Replace appropriate values in config.py, service.py and run below command to invoke service" \
                   "   - python service.py" \
        },
    "config": {
        "extension": ".py",
        "content": 'PRIVATE_KEY = "<your wallet\'s private key>"\n' \
                   f'ETH_RPC_ENDPOINT = "https://{settings.network.networks[settings.network.id].name}.infura.io/v3/<your infura key>"\n'
                   f'ORG_ID = "org_id_placeholder"\n' \
                   f'SERVICE_ID = "service_id_placeholder"\n'
    },
    "service": {
        "extension": ".py",
        "content": SERVICE_PY_CONTENT
    }
}


TEMP_FILE_DIR = tempfile.gettempdir()
