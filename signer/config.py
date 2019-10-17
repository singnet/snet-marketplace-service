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
GET_FREE_CALLS_METERING_ARN = ""
PREFIX_FREE_CALL = ""
NET_ID = 0
SLACK_HOOK = {
    "hostname": "",
    "port": 443,
    "path": "",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
}
signer = {}
# this configuration is only for testing
SIGNER_KEY = "5d66dccb32b03871f30533fe410d2e5998d607a579fb7bc2d991cd2148e3ec69"
SIGNER_ADDRESS = "0xBBE343b9BEf87Fb687cA83A014324d5E52cc3754"
REGION_NAME = ""
