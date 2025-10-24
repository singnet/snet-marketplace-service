NETWORKS = {
    11155111: {
        "name": "test",
        "http_provider": "https://sepolia.infura.io",
        "ws_provider": "wss://sepolia.infura.io/ws",
        "db": {
            "DB_DRIVER": "mysql+pymysql",
            "DB_HOST": "localhost",
            "DB_USER": "unittest_root",
            "DB_PASSWORD": "unittest_pwd",
            "DB_NAME": "contract_api_unittest_db",
            "DB_PORT": 3306,
        },
    }
}
NETWORK_ID = 11155111
TOKEN_NAME = "FET"
STAGE = "dev"

SLACK_HOOK = {
    'hostname': 'https://hooks.slack.com',
    'path': ''
}
IPFS_URL = {
    'url': 'ipfs.singularitynet.io',
    'port': '80',

}
REGION_NAME = ""
S3_BUCKET_ACCESS_KEY = ""
S3_BUCKET_SECRET_KEY = ""
ASSETS_BUCKET_NAME = ""
PATH_PREFIX = "/EthAccounts/ropsten/"
ASSETS_PREFIX = ""
GET_SERVICE_FROM_ORGID_SERVICE_ID_REGISTRY_ARN = ""
MARKETPLACE_DAPP_BUILD = ""
ASSET_TEMP_EXTRACT_DIRECTORY = "/var/task/"
ASSETS_COMPONENT_BUCKET_NAME = ""
MANAGE_PROTO_COMPILATION = ""
GET_STATE_SERVICE_SIGNATURE_ARN = ""
CONTRACT_BASE_PATH = ""