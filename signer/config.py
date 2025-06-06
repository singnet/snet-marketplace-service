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
        "name": "test",
        "http_provider": "https://sepolia.infura.io/v3/98064002908248a0b0d837940d2c647b",
        "ws_provider": "wss://sepolia.infura.io/ws/v3/98064002908248a0b0d837940d2c647b",
        "contract_base_path": ".",
    }
}

SLACK_HOOK: SlackHookConfigDict = {"hostname": "https://hooks.slack.com", "path": ""}

DB_CONFIG: DBConfigDict = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "root",
    "password": "",
    "name": "signer",
    "port": 3306,
}

SIGNER: SignerConfigDict = {
    "key": "a22bc5d20a680ca810df36bd00f9017dabea3743f5cf2cbfae5d7415f3e0564b",
    "address": "0x5CAe9719df1a1Fc890303500F658b65bE0817C4B",
    "expiration_block_count": 100,
}

AWS: AWSConfigDict = {
    "region_name": "us-east-1",
}

LAMBDA_ARN: LambdaARNConfigDict = {
    "get_service_details_arn": "",
}
