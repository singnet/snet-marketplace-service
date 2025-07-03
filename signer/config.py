from typing import Dict, TypedDict


class NetworkConfigDict(TypedDict):
    name: str
    http_provider: str
    ws_provider: str
    contract_base_path: str


class SlackHookConfigDict(TypedDict):
    hostname: str
    path: str


class DBConfigDict(TypedDict):
    driver: str
    host: str
    user: str
    password: str
    name: str
    port: int


class SignerConfigDict(TypedDict):
    key: str
    address: str
    expiration_block_count: int


class AWSConfigDict(TypedDict):
    region_name: str


class LambdaARNConfigDict(TypedDict):
    get_service_details_arn: str


NETWORK_ID = 11155111
TOKEN_NAME = "FET"
STAGE = "dev"

NETWORKS: Dict[int, NetworkConfigDict] = {
    11155111: {
        "name": "sepolia",
        "http_provider": "",
        "ws_provider": "",
        "contract_base_path": ".",
    }
}

SLACK_HOOK: SlackHookConfigDict = {"hostname": "https://hooks.slack.com", "path": ""}

DB_CONFIG: DBConfigDict = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "unittest_root",
    "password": "unittest_pwd",
    "name": "signer_unittest_db",
    "port": 3306
}

SIGNER: SignerConfigDict = {
    "key": "5d66dccb32b03871f30533fe410d2e5998d607a579fb7bc2d991cd2148e3ec69",
    "address": "0xBBE343b9BEf87Fb687cA83A014324d5E52cc3754",
    "expiration_block_count": 100,
}

AWS: AWSConfigDict = {
    "region_name": "us-east-1",
}

LAMBDA_ARN: LambdaARNConfigDict = {
    "get_service_details_arn": "",
}
