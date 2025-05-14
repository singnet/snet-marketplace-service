NETWORKS = {
    11155111: {
        "name": "test",
        "http_provider": "https://sepolia.infura.io",
        "ws_provider": "wss://sepolia.infura.io/ws",
        "ContractBasePath": "",
    }
}

NETWORK_ID = 3
TOKEN_NAME = ""
STAGE = ""

DB_CONFIG = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "unittest_root",
    "password": "unittest_pwd",
    "name": "registry_unittest_db",
    "port": 3306
}

SLACK_HOOK = {
    "hostname": "https://hooks.slack.com",
    "path": ""
}

IPFS_URL = {
    "url": "ipfs.singularitynet.io",
    "port": "80",
}

EMAILS = {
    "PUBLISHER_PORTAL_SUPPORT_MAIL": "",
    "ORG_APPROVERS_DLIST": "",
    "SERVICE_APPROVERS_DLIST": ""
}

AWS = {
    "ALLOWED_ORIGIN": ["PUBLISHER"],
    "REGION_NAME": "us-east-1",
    "S3": {
        "ASSET_BUCKET": "snet-marketplace-assets",
        "ASSET_DIR": "/tmp",
        "UPLOAD_BUCKET": {
            "ORG_BUCKET": "org_bucket"
        },
        "ASSET_COMPONENT_BUCKET_NAME": "snet-marketplace-assets",
        "ALLOWED_HERO_IMAGE_FORMATS": [".jpg", ".jpeg", ".png"],
    }
}

LAMBDA_ARN = {
    "NOTIFICATION_ARN": "",
    "VERIFICATION_ARN": {
        "DUNS_CALLBACK": "",
        "GET_VERIFICATION": ""
    },
    "SERVICE_CURATE_ARN": "",
    "DEMO_COMPONENT": {
        "CODE_BUILD_NAME": "",
        "UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN": ""
    },
    "MANAGE_PROTO_COMPILATION_LAMBDA_ARN": "",
    "PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT": "",
    "GET_SERVICE_FOR_GIVEN_ORG_ENDPOINT": ""
}


DEMO_COMPONENT_CODE_BUILD_NAME = ""
UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN = ""
MANAGE_PROTO_COMPILATION_LAMBDA_ARN = ""
ALLOWED_HERO_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']
PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT = ""
GET_SERVICE_FOR_GIVEN_ORG_ENDPOINT = ""
ASSETS_COMPONENT_BUCKET_NAME = ""
CONTRACT_BASE_PATH = ""
GET_SERVICE_FOR_GIVEN_ORG_ARN = {
    "FET": "",
    "AGIX": ""
}
PUBLISH_OFFCHAIN_ATTRIBUTES_ARN = {
    "FET": "",
    "AGIX": ""
}

