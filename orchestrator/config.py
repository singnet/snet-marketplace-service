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
NETWORK_ID = 0
CREATE_ORDER_SERVICE_ARN = ""
INITIATE_PAYMENT_SERVICE_ARN = ""
EXECUTE_PAYMENT_SERVICE_ARN = ""
CREATE_AND_REGISTER_WALLET_ARN = "" # POST /wallet
CHANNEL_ADD_FUNDS_ARN = "" # POST /wallet/channel/deposit
GET_CHANNEL_TRANSACTIONS_ARN = "" # GET /wallet/channel/transactions
REGISTER_WALLET_ARN = "" # POST /wallet/register
GET_WALLETS_ARN = "" # GET /wallet
SET_DEFAULT_WALLET_ARN = "" # POST /wallet/status
CREATE_CHANNEL_ARN = "" # +
CREATE_CHANNEL_EVENT_ARN = "" # +
DAPP_USER_SERVICE_ARN = ""
CONTRACT_API_SERVICE_ARN = ""
SIGNER_SERVICE_ARN = ""
SLACK_HOOK = {}
CONTRACT_API_ARN = ""
ORDER_DETAILS_ORDER_ID_ARN = ""
ORDER_DETAILS_BY_USERNAME_ARN = ""
REGION_NAME = "us-east-2"
SIGNER_ADDRESS = ""
EXECUTOR_ADDRESS = ""
ORDER_EXPIRATION_THRESHOLD_IN_MINUTES = 15
GET_CHANNELS_FOR_GROUP = ""
GET_GROUP_FOR_ORG_API_ARN = ""
GET_ALL_ORG_API_ARN = ""
USD_TO_COGS_CONVERSION_FACTOR = 1
REGISTRY_ARN = {
    "REGISTER_MEMBER_ARN": "",
    "CREATE_ORG_ARN": ""
}
VERIFICATION_ARN = {
    "INITIATE": ""
}
SLACK_CHANNEL_FOR_APPROVAL_TEAM = ""
NOTIFICATION_ARN = ""
ORG_APPROVERS_DLIST = ""
