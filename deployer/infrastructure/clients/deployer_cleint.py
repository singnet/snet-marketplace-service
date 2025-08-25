import json
from typing import Optional

import boto3

from common.logger import get_logger
from deployer.config import (
    REGION_NAME,
    START_DAEMON_ARN,
    DELETE_DAEMON_ARN,
    UPDATE_DAEMON_STATUS_ARN,
    REDEPLOY_DAEMON_ARN,
)


logger = get_logger(__name__)


class DeployerClientError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Deployer Client response error: {message}")


class DeployerClient:
    def __init__(self):
        self._lambda_client = boto3.client("lambda", region_name=REGION_NAME)

    def _invoke_lambda(
        self,
        lambda_function_arn: str,
        headers: Optional[dict] = None,
        path_parameters: Optional[dict] = None,
        query_parameters: Optional[dict] = None,
        body: Optional[dict] = None,
        asynchronous=False,
    ) -> Optional[dict]:
        payload = {}
        if path_parameters:
            payload["pathParameters"] = path_parameters
        if query_parameters:
            payload["queryStringParameters"] = query_parameters
        if body:
            payload["body"] = json.dumps(body)
        if headers:
            payload["headers"] = headers
        try:
            response = self._lambda_client.invoke(
                FunctionName=lambda_function_arn,
                InvocationType="Event" if asynchronous else "RequestResponse",
                Payload=json.dumps(payload),
            )

            if not asynchronous:
                response_body = json.loads(json.loads(response.get("Payload").read())["body"])
                if response_body["status"] == "success":
                    return response_body["data"]
                else:
                    raise DeployerClientError(response_body)
            elif response["ResponseMetadata"]["HTTPStatusCode"] != 202:
                raise DeployerClientError(response)

        except Exception as e:
            raise DeployerClientError(str(e))

    def start_daemon(self, daemon_id: str, asynchronous=False):
        return self._invoke_lambda(
            lambda_function_arn=START_DAEMON_ARN,
            path_parameters={"daemon_id": daemon_id},
            asynchronous=asynchronous,
        )

    def stop_daemon(self, daemon_id: str, asynchronous=False):
        return self._invoke_lambda(
            lambda_function_arn=DELETE_DAEMON_ARN,
            path_parameters={"daemon_id": daemon_id},
            asynchronous=asynchronous,
        )

    def redeploy_daemon(self, daemon_id: str, asynchronous=False):
        return self._invoke_lambda(
            lambda_function_arn=REDEPLOY_DAEMON_ARN,
            path_parameters={"daemon_id": daemon_id},
            asynchronous=asynchronous,
        )

    def update_daemon_status(self, daemon_id: str, asynchronous=False):
        return self._invoke_lambda(
            lambda_function_arn=UPDATE_DAEMON_STATUS_ARN,
            path_parameters={"daemon_id": daemon_id},
            asynchronous=asynchronous,
        )
