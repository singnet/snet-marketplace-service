import json

import boto3
from dapp_user.settings import settings


class ContractAPIClientError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Contract API Client response error: {message}")


class ContractAPIClient:
    def __init__(self):
        self.lambda_client = boto3.client("lambda", region_name=settings.aws.region_name)

    def update_service_rating(
        self,
        org_id: str,
        service_id: str,
        rating: float,
        total_users_rated: int,
    ) -> None:
        try:
            lambda_payload = {
                "httpMethod": "GET",
                "pathParameters": {"orgId": org_id, "serviceId": service_id},
                "body": json.dumps(
                    {
                        "rating": rating,
                        "total_users_rated": total_users_rated,
                    }
                ),
            }

            response = self.lambda_client.invoke(
                FunctionName=settings.lambda_arn.update_service_rating_arn,
                InvocationType="RequestResponse",
                Payload=json.dumps(lambda_payload),
            )

            response_body_raw = json.loads(response.get("Payload").read())["body"]
            get_service_response = json.loads(response_body_raw)
            if get_service_response["status"] != "success":
                message = get_service_response.get("message", "Unknown error occurred")
                raise ContractAPIClientError(message=message)

        except Exception as e:
            raise ContractAPIClientError(str(e))
