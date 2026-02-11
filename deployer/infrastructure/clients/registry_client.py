from typing import List

from common.lambda_client import LambdaClient
from deployer.config import REGION_NAME, GET_ALL_ORGS_ARN


class RegistryClient(LambdaClient):
    def __init__(self):
        super().__init__(REGION_NAME)

    def get_all_orgs(self, username: str, account_id: str, origin: str) -> List[dict]:
        return self._invoke_lambda(
            lambda_function_arn=GET_ALL_ORGS_ARN,
            authorizer_email=username,
            authorizer_sub=account_id,
            origin=origin,
            asynchronous=False,
        )
