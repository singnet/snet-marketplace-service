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
            "DB_NAME": "unittest_db",
            "DB_PORT": 3306,
        },
    }
}

SLACK_HOOK = {
    'hostname': 'https://hooks.slack.com',
    'path': ''
}
IPFS_URL = {
    'url': '',
    'port': '80',

}
NETWORK_ID = 3
REGION_NAME = "us-east-2"
S3_BUCKET_ACCESS_KEY = ""
S3_BUCKET_SECRET_KEY = ""
ASSETS_BUCKET_NAME = ""
PATH_PREFIX = "/EthAccounts/ropsten/"
ASSETS_PREFIX = ""
GET_SERVICE_FROM_ORGID_SERVICE_ID_REGISTRY_ARN = ""
MARKETPLACE_DAPP_BUILD = ""
ASSET_TEMP_EXTRACT_DIRECTORY = "/var/task/"
ASSETS_COMPONENT_BUCKET_NAME = ""
PUSH_MEDIA_TO_S3_USING_HASH_LAMBDA_ARN = ""