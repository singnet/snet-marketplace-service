import json

import boto3
from dapp_user.settings import settings


class WalletsAPIClientError(Exception):
    pass


class DeleteUserWalletError(WalletsAPIClientError):
    def __init__(self, message: str):
        super().__init__(message)


class WalletsAPIClient:
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

            response_body_raw = json.loads(response.get("Payload").read())["body"]
            delete_user_wallet_response = json.loads(response_body_raw)
        except Exception as e:
            raise DeleteUserWalletError(f"Failed to invoke delete user wallet lambda: {str(e)}")

        if delete_user_wallet_response["status"] == "success":
            return True
        return False