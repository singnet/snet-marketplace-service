NETWORK_ID = 11155111
TOKEN_NAME = ""
STAGE = "LOCAL"

NETWORKS = {
    11155111: {
        "name": "test",
        "http_provider": "https://sepolia.infura.io",
        "ws_provider": "wss://sepolia.infura.io/ws",
        "contract_base_path": "",
    }
}

SLACK_HOOK = {
    "hostname": "https://hooks.slack.com",
    "path": ""
}

DB_CONFIG = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "unittest_root",
    "password": "unittest_pwd",
    "name": "unittest_db",
    "port": 3306
}

SIGNER = {
    "KEY": "5d66dccb32b03871f30533fe410d2e5998d607a579fb7bc2d991cd2148e3ec69" ,
    "ADDRESS": "0xBBE343b9BEf87Fb687cA83A014324d5E52cc3754",
}

AWS = {
    "REGION_NAME": "us-east-1",
}

LAMBDA_ARN = {
    "GET_SERVICE_DETAILS_FOR_GIVEN_ORG_ID_AND_SERVICE_ID_ARN": "",
    "PREFIX_FREE_CALL": "",
    "METERING_ARN": "",

}

CONTRACT_BASE_PATH = "/opt/"

