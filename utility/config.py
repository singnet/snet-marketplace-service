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
    'path': ''
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

CRYPTO_FIAT_CONVERSION = {
    'EXCHANGE': 'COINMARKETCAP',
    'RATE_THRESHOLD': 10,
    'MULTIPLIER': 1.5,
    'CURRENT_AGI_USD_RATE': 0.30045,
    'LIMIT': 4,
    'COINMARKETCAP': {
        'API_ENDPOINT': 'https://pro-api.coinmarketcap.com/v2/tools/price-conversion?amount=1&convert={}&symbol={}'
    }
}