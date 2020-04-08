import json

import requests

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
    generate_lambda_response(200, "OK")

