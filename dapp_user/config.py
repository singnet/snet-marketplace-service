from dapp_user.constant import SourceDApp
NETWORKS = {
    3: {
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
GET_FREE_CALLS_METERING_ARN = ""
PATH_PREFIX = ""
SLACK_HOOK = {
    'hostname': '',
    'path': ''
}
CONTRACT_API_ARN = ""
DELETE_USER_WALLET_ARN = ""
REGION_NAME = "us-east-2"
NETWORK_ID = 3
GET_SIGNATURE_TO_GET_FREE_CALL_FROM_DAEMON = {}
CALLER_REFERENCE = {
    "dummy_client_id_1": SourceDApp.PUBLISHER_DAPP.value,
    "dummy_client_id_2": SourceDApp.MARKETPLACE_DAPP.value,
    "dummy_client_id_3": SourceDApp.TOKEN_STAKE_DAPP.value,
    "dummy_client_id_4": SourceDApp.RFAI_DAPP.value
}
