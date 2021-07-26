NETWORKS = {
    3: {
        "name": "test",
        "http_provider": "https://ropsten.infura.io",
        "ws_provider": "wss://ropsten.infura.io/ws",
        "db": {
            "DB_DRIVER": "mysql+pymysql",
            "DB_HOST": "localhost",
            "DB_USER": "unittest_root",
            "DB_PASSWORD": "unittest_pwd",
            "DB_NAME": "registry_unittest_db",
            "DB_PORT": 3306,
        },
    }
}
NETWORK_ID = 3
SLACK_HOOK = {
    'hostname': 'https://hooks.slack.com',
    'path': ''
}
IPFS_URL = {
    'url': 'ipfs.singularitynet.io',
    'port': '80',

}
ALLOWED_ORIGIN = ["PUBLISHER"]
METADATA_FILE_PATH = "/tmp"
REGION_NAME = "us-east-1"
ASSET_BUCKET = ""
ASSET_DIR = "/tmp"
NOTIFICATION_ARN = ""
PUBLISHER_PORTAL_DAPP_URL = ""
UPLOAD_BUCKET = {
    "ORG_BUCKET": "org_bucket"
}
VERIFICATION_ARN = {
    "DUNS_CALLBACK": "",
    "GET_VERIFICATION": ""
}
EMAILS = {
    "PUBLISHER_PORTAL_SUPPORT_MAIL": "",
    "ORG_APPROVERS_DLIST": "",
    "SERVICE_APPROVERS_DLIST": ""
}
SERVICE_CURATE_ARN = ""
APPROVAL_SLACK_HOOK = {
    'hostname': 'https://hooks.slack.com',
    'path': ''
}
DEMO_COMPONENT_CODE_BUILD_NAME = ""
UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN = ""
MANAGE_PROTO_COMPILATION_LAMBDA_ARN = ""
ALLOWED_HERO_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']
PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT = ""
GET_SERVICE_FOR_GIVEN_ORG_ENDPOINT = ""