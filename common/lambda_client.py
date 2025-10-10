import json
import os
from typing import Optional, Union

import boto3


class LambdaClientError(Exception):
    def __init__(self, lambda_client_name: str, message: str):
        super().__init__(f"{lambda_client_name} response error: {message}")


class LambdaClient:
    def __init__(self, region_name: str):
        if os.environ.get("IS_SERVERLESS_OFFLINE") == "true": # for local building and running
            self._boto_client = boto3.client("lambda", region_name = region_name,
                                             endpoint_url = "http://localhost:3000", aws_access_key_id = "mock",
                                             aws_secret_access_key = "mock")
        else:
            self._boto_client = boto3.client('lambda', region_name=region_name)

    def _invoke_lambda(
        self,
        lambda_function_arn: str,
        headers: Optional[dict] = None,
        path_parameters: Optional[dict] = None,
        query_parameters: Optional[dict] = None,
        body: Optional[dict] = None,
        authorizer_email: Optional[str] = None,
        authorizer_sub: Optional[str] = None,
        origin: Optional[str] = None,
        asynchronous=False,
    ) -> Union[dict, list, None]:
        payload = {}
        if path_parameters is not None:
            payload["pathParameters"] = path_parameters
        if query_parameters is not None:
            payload["queryStringParameters"] = query_parameters
        if body is not None:
            payload["body"] = json.dumps(body)
        if headers is None:
            headers = {}
        if "origin" not in headers and "Origin" not in headers and origin is not None:
            headers["origin"] = origin
        payload["headers"] = headers

        if authorizer_email is not None or authorizer_sub is not None:
            payload["requestContext"] = {"authorizer": {"claims": {}}}
            if authorizer_email is not None:
                payload["requestContext"]["authorizer"]["claims"]["email"] = authorizer_email
            if authorizer_sub is not None:
                payload["requestContext"]["authorizer"]["claims"]["sub"] = authorizer_sub

        try:
            response = self._boto_client.invoke(
                FunctionName=lambda_function_arn,
                InvocationType="Event" if asynchronous else "RequestResponse",
                Payload=json.dumps(payload),
            )

            if not asynchronous:
                response_body = json.loads(json.loads(response.get("Payload").read())["body"])
                if response_body["status"] == "success":
                    return response_body["data"]
                else:
                    raise LambdaClientError(self.__class__.__name__, response_body)
            elif response["ResponseMetadata"]["HTTPStatusCode"] != 202:
                raise LambdaClientError(self.__class__.__name__, response)

        except Exception as e:
            raise LambdaClientError(self.__class__.__name__, str(e))