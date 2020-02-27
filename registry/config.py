NETWORKS = {
    3: {
        "name": "test",
        "http_provider": "https://ropsten.infura.io/v3/09027f4a13e841d48dbfefc67e7685d5",
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
    'hostname': '',
    'port': 443,
    'path': '',
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    }
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
EXECUTOR_ADDRESS = "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F"
EXECUTOR_KEY = "5d66dccb32b03871f30533fe410d2e5998d607a579fb7bc2d991cd2148e3ec67"
ORG_ID_FOR_TESTING_AI_SERVICE = "curation"
