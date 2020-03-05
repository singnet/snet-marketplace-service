import requests
import json
import boto3

from event_pubsub.config import REGION_NAME


class ListenersHandlers(object):

    def push_event(self):
        pass


class WebHookHandler(ListenersHandlers):

    def __init__(self, url):
        self.url = url

    def push_event(self, data):
        try:
            requests.post(self.url, data)
        except Exception as e:
            print(e)
            raise e


class LambdaArnHandler(ListenersHandlers):
    lambda_client = boto3.client('lambda',region_name=REGION_NAME)

    def __init__(self, arn):
        self.arn = arn

    def push_event(self, data):
        try:

            response = self.lambda_client.invoke(
                FunctionName=self.arn,
                InvocationType='RequestResponse',
                Payload=json.dumps(data)
            )
            response_data = json.loads(response.get('Payload').read())
            if response_data['statusCode'] != 200:
                raise Exception(response_data['body'])
        except Exception as e:
            print(e)
            raise e
