import json
from http import HTTPStatus

import boto3
from common.constant import TokenSymbol
from common.exceptions import WrongTokenSymbolException
from dapp_user.domain.interfaces.contract_api_client_interface import AbstractContractAPIClient
from dapp_user.settings import settings


class ContractAPIClientError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Contract API Client response error: {message}")


class ContractAPIClient(AbstractContractAPIClient):
    def __init__(self):
        self.lambda_client = boto3.client("lambda", region_name=settings.aws.region_name)

    def update_service_rating(
        self,
        org_id: str,
        service_id: str,
        rating: float,
        total_users_rated: int,
        token_name: TokenSymbol,
    ) -> None:
        try:
            lambda_payload = {
                "pathParameters": {"org_id": org_id, "service_id": service_id},
                "body": json.dumps(
                    {
                        "rating": rating,
                        "total_users_rated": total_users_rated,
                    }
                ),
            }

            lambda_arn: str = ""
            if token_name == TokenSymbol.FET:
                lambda_arn = settings.lambda_arn.update_service_rating_arn.fet
            elif token_name == TokenSymbol.AGIX:
                lambda_arn = settings.lambda_arn.update_service_rating_arn.agix
            else:
                raise WrongTokenSymbolException()

            response = self.lambda_client.invoke(
                FunctionName=lambda_arn,
                InvocationType="RequestResponse",
                Payload=json.dumps(lambda_payload),
            )

            if response["StatusCode"] != HTTPStatus.OK:
                raise ContractAPIClientError(message=response["FunctionError"])

        except Exception as e:
            raise ContractAPIClientError(str(e))
