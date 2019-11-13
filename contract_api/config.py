NETWORKS = {3: {
    'http_provider': 'https://ropsten.infura.io/',
    'ws_provider': 'wss://ropsten.infura.io/',
    'db': {"DB_HOST": "localhost",
           "DB_USER": "root",
           "DB_PASSWORD": "password",
           "DB_NAME": "pub_sub",
           "DB_PORT": 3306,
           }
}}

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
NETWORK_ID = 3
REGION_NAME = ""
S3_BUCKET_ACCESS_KEY = ""
S3_BUCKET_SECRET_KEY = ""
ASSETS_BUCKET_NAME = ""
PATH_PREFIX = "/EthAccounts/ropsten/"
ASSETS_PREFIX = ""
