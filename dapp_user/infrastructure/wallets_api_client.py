import json
from http import HTTPStatus

import boto3
from common.constant import TokenSymbol
from common.exceptions import WrongTokenSymbolException
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

    def delete_user_wallet(self, username: str, token_name: TokenSymbol) -> bool:
        lambda_payload = {
            "httpMethod": "DELETE",
            "pathParameters": {"username": username},
        }

        lambda_arn: str = ""
        if token_name == TokenSymbol.FET:
            lambda_arn = settings.lambda_arn.update_service_rating_arn.fet
        elif token_name == TokenSymbol.AGIX:
            lambda_arn = settings.lambda_arn.update_service_rating_arn.agix
        else:
            raise WrongTokenSymbolException()

        try:
            response = self.lambda_client.invoke(
                FunctionName=lambda_arn,
                InvocationType="RequestResponse",
                Payload=json.dumps(lambda_payload),
            )
        except Exception as e:
            raise DeleteUserWalletError(f"Failed to invoke delete user wallet lambda: {str(e)}")

        logger.debug(f"Delete user wallet response: {response}")
        return response["StatusCode"] == HTTPStatus.OK
