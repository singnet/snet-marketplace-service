MODE = 'sandbox'
PAYPAL_CLIENT = ''
PAYPAL_SECRET = ''
PAYMENT_RETURN_URL = ""
PAYMENT_CANCEL_URL = ""
SLACK_HOOK = {}
REGION_NAME = "us-east-2"
NETWORK_ID = 0
NETWORK = {
    "name": "test",
    "http_provider": "https://ropsten.infura.io",
    "ws_provider": "wss://ropsten.infura.io/ws",
    "db": {
        "DB_HOST": "localhost",
        "DB_USER": "unittest_root",
        "DB_PASSWORD": "unittest_pwd",
        "DB_NAME": "unittest_db",
        "DB_PORT": 3306
    }
}
DB_URL = f'mysql+pymysql://{NETWORK["db"]["DB_USER"]}:{NETWORK["db"]["DB_PASSWORD"]}@{NETWORK["db"]["DB_HOST"]}/{NETWORK["db"]["DB_NAME"]}'
