import tempfile
from enum import Enum

from utility.config import UPLOAD_BUCKET, NETWORKS, NETWORK_ID


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

ETHERIUM_NETWORK_NAMES = {
    "1": "mainnet",
    "3": "ropsten"
}

PYTHON_BOILERPLATE_TEMPLATE = {
    "requirement": {
        "extension": ".txt",
        "content": "snet.sdk\nsnet-cli"
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
                   f'ETH_RPC_ENDPOINT = "https://{ETHERIUM_NETWORK_NAMES[str(NETWORK_ID)]}.infura.io/v3/<your infura key>"\n'
                   f'ORG_ID = "org_id_placeholder"\n' \
                   f'SERVICE_ID = "service_id_placeholder"\n'
    },
    "service": {
        "extension": ".py",
        "content":
            'from snet.sdk import SnetSDK\n' \
            'import config\n' \
            'import stub_placeholder_pb2\n' \
            'import stub_placeholder_pb2_grpc\n\n' \
            'def invoke_service():\n' \
            '   snet_config = {"private_key": config.PRIVATE_KEY, "eth_rpc_endpoint": config.ETH_RPC_ENDPOINT}\n' \
            '   sdk = SnetSDK(config=snet_config)\n' \
            '   service_client = sdk.create_service_client(\n' \
            '      org_id=config.ORG_ID,\n' \
            '      service_id=config.SERVICE_ID,\n' \
            '      service_stub= stub_placeholder_pb2_grpc.service_stub # replace service_stub\n' \
            '   )\n' \
            '   request = stub_placeholder_pb2.input_method(arguments) # replace input_method and arguments\n' \
            '   response = service_client.service.service_method(request) # replace service_method\n'
            '   print(f"service invoked successfully :: response :: {response}")\n\n\n'
            'invoke_service() # call invoke service method'
    }
}

TEMP_FILE_DIR = tempfile.gettempdir()
