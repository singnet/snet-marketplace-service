NETWORKS = {
    0: {
        "name": "test",
        "http_provider": "https://ropsten.infura.io/v3/6d5b19d45cbc45699d2ec1c12a7e572b",
        "ws_provider": "wss://ropsten.infura.io/ws",
        "db": {
            "DB_DRIVER": "mysql+pymysql",
            "DB_HOST": "localhost",
            "DB_USER": "d",
            "DB_PASSWORD": "123",
            "DB_NAME": "wallet",
            "DB_PORT": 3306,
        },
    }
}
DB_DETAILS = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "d",
    "password": "123",
    "name": "wallet",
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
GET_MPE_PROCESSED_TRANSACTION_ARN = ""