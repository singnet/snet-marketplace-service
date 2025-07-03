import json
from http import HTTPStatus

import boto3
from common.logger import get_logger
from dapp_user.domain.interfaces.wallet_api_client_interface import AbstractWalletsAPIClient
from dapp_user.settings import settings

logger = get_logger(__name__)


class WalletsAPIClientError(Exception):
    pass


class DeleteUserWalletError(WalletsAPIClientError):
    def __init__(self, message: str):
        super().__init__(message)


class WalletsAPIClient(AbstractWalletsAPIClient):
    def __init__(self):
        self.lambda_client = boto3.client("lambda", region_name=settings.aws.region_name)

    def delete_user_wallet(self, username: str) -> bool:
        lambda_payload = {
            "httpMethod": "DELETE",
            "pathParameters": {"username": username},
        }

        try:
            response = self.lambda_client.invoke(
                FunctionName=settings.lambda_arn.delete_user_wallet_arn,
                InvocationType="RequestResponse",
                Payload=json.dumps(lambda_payload),
            )
        except Exception as e:
            raise DeleteUserWalletError(f"Failed to invoke delete user wallet lambda: {str(e)}")

        logger.debug(f"Delete user wallet response: {response}")
        return response["StatusCode"] == HTTPStatus.OK
