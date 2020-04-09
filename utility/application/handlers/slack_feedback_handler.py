import json

import requests

from common.constant import StatusCode
from common.utils import generate_lambda_response
from utility.config import SLACK_FEEDBACK_HOOK


def main(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_parameters = event["queryStringParameters"]

    client = query_parameters['client']
    slack_hook = SLACK_FEEDBACK_HOOK[client]
    body = json.loads(event['body'])
    body['username'] = username
    requests.post(slack_hook, data=json.dumps(body))
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": {"message": "ok" }, "error": {}}, cors_enabled=True
    )

