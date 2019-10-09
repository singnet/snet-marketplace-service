import json

import boto3


class BotoUtils:
    def __init__(self, region_name):
        self.region_name = region_name

    def get_ssm_parameter(self, parameter):
        ssm = boto3.client("ssm", region_name=self.region_name)
        parameter = ssm.get_parameter(Name=parameter, WithDecryption=True)
        return parameter["Parameter"]["Value"]

    def invoke_lambda(self, lambda_function_arn, invocation_type, payload):
        lambda_client = boto3.client("lambda", region_name=self.region_name)
        lambda_response = lambda_client.invoke(
            FunctionName=lambda_function_arn,
            InvocationType=invocation_type,
            Payload=payload,
        )
        return json.loads(lambda_response.get("Payload").read())
