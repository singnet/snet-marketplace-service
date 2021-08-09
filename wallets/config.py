NETWORKS = {
    0: {
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
DB_DETAILS = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "unittest_root",
    "password": "unittest_pwd",
    "name": "unittest_db",
    "port": 3306
}
SIGNER_KEY = ""
SIGNER_ADDRESS = ""
EXECUTOR_KEY = ""
EXECUTOR_ADDRESS = ""
NETWORK_ID = 0
SLACK_HOOK = {}
REGION_NAME = "us-east-2"
WALLET_TYPES_ALLOWED = []
MINIMUM_AMOUNT_IN_COGS_ALLOWED = 0
GET_RAW_EVENT_DETAILS = ""