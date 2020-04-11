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
    'hostname': '',
    'port': 443,
    'path': '',
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    }
}
REGION_NAME = ""
UPLOAD_BUCKET = {
    "FEEDBACK_BUCKET": "",
    "ORG_BUCKET": ""
}
ALLOWED_CONTENT_TYPE = []
FILE_EXTENSION = {}
SLACK_FEEDBACK_HOOK = {
    "MARKETPLACE": "",
    "RFAI": "",
    "STAKING": ""
}
