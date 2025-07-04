from typing import Dict, TypedDict


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


class AWSConfigDict(TypedDict):
    region_name: str
    cognito_pool: str


class DeleteUserWalletDict(TypedDict):
    fet: str
    agix: str


class UpdateServiceRatingDict(TypedDict):
    fet: str
    agix: str


class LambdaARNConfigDict(TypedDict):
    delete_user_wallet_arn: DeleteUserWalletDict
    update_service_rating_arn: UpdateServiceRatingDict


STAGE = "dev"

SLACK_HOOK: SlackHookConfigDict = {"hostname": "https://hooks.slack.com", "path": ""}

DB_CONFIG: DBConfigDict = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "unittest_root",
    "password": "unittest_pwd",
    "name": "dapp_user_unittest_db",
    "port": 3306,
}


AWS: AWSConfigDict = {
    "region_name": "us-east-1",
    "cognito_pool": "us-east-1_xxxxxx",
}

LAMBDA_ARN: LambdaARNConfigDict = {
    "delete_user_wallet_arn": {
        "fet": "",
        "agix": "",
    },
    "update_service_rating_arn": {
        "fet": "",
        "agix": "",
    },
}

CALLER_REFERENCE: Dict[str, str] = {
    "dummy_client_id_1": "PUBLISHER_DAPP",
    "dummy_client_id_2": "MARKETPLACE_DAPP",
}
