import json
from typing import Tuple

import boto3
from signer.settings import settings


class ContractAPIClientError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Contract API Client response error: {message}")


class ContractAPIClient:
    def __init__(self):
        self.lambda_client = boto3.client("lambda", region_name=settings.aws.region_name)

    def get_daemon_endpoint_and_free_call_for_group(
        self, org_id: str, service_id: str, group_id: str
    ) -> Tuple[str, int]:
        lambda_payload = {
            "pathParameters": {"orgId": org_id, "serviceId": service_id},
        }

        response = self.lambda_client.invoke(
            FunctionName=settings.lambda_arn.get_service_details_arn,
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload),
        )

        response_body_raw = json.loads(response.get("Payload").read())["body"]
        get_service_response = json.loads(response_body_raw)
        if get_service_response["status"] == "success":
            groups_data = get_service_response["data"].get("groups", [])
            for group_data in groups_data:
                if group_data["groupId"] == group_id:
                    return group_data["endpoints"][0]["endpoint"], group_data.get("freecalls", 0)
        raise ContractAPIClientError(
            message=f"Unable to fetch daemon Endpoint information for service {service_id} under organization {org_id} for {group_id} group."
        )
