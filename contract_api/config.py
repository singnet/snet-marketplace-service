NETWORKS = {
    0: {
        "name": "test",
        "http_provider": "https://ropsten.infura.io",
        "ws_provider": "wss://ropsten.infura.io/ws",
        "db": {
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
    'port': 443,
    'path': '',
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    }
}
IPFS_URL = {
    'url': '',
    'port': '80',

}
NETWORK_ID = 0
REGION_NAME = ""
S3_BUCKET_ACCESS_KEY = ""
S3_BUCKET_SECRET_KEY = ""
ASSETS_BUCKET_NAME = ""
PATH_PREFIX = "/EthAccounts/ropsten/"
ASSETS_PREFIX = ""
