import json
import boto3
from signer.settings import settings


class ContractAPIClient:
    def __init__(self):
        self.lambda_client = boto3.client("lambda", region_name=settings.aws.REGION_NAME)

    def get_daemon_endpoint_and_free_call_for_group(
        self, org_id: str, service_id: str, group_id: str
    ):
        lambda_payload = {
            "httpMethod": "GET",
            "pathParameters": {"orgId": org_id, "serviceId": service_id},
        }

        response = self.lambda_client.invoke(
            FunctionName=settings.lambda_arn.get_service_deatails_arn,
            InvocationType="RequestResponse",
            Payload=json.dumps(lambda_payload),
        )

        response_body_raw = json.loads(response.get("Payload").read())["body"]
        get_service_response = json.loads(response_body_raw)
        if get_service_response["status"] == "success":
            groups_data = get_service_response["data"].get("groups", [])
            for group_data in groups_data:
                if group_data["group_id"] == group_id:
                    return group_data["endpoints"][0]["endpoint"], group_data.get("free_calls", 0)
        raise Exception(
            "Unable to fetch daemon Endpoint information for service %s under organization %s for %s group.",
            service_id,
            org_id,
            group_id,
        )
