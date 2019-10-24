import requests
import json


class ListenersHandlers(object):

    def push_event(self):
        pass


class WebHookHandler(ListenersHandlers):

    def __init__(self, url, data):
        self.url = url
        self.data = data

    def push_event(self):
        try:
            requests.post(self.url, self.data)
        except Exception as e:
            print(e)
            raise e


class LambdaArnHandler(ListenersHandlers):
    def __init__(self, arn, data):
        self.arn = arn
        self.data = data

    def push_event(self):

        try:

            response = self.lambda_client.invoke(
                FunctionName=self.arn,
                InvocationType='RequestResponse',
                Payload=json.dumps(self.data)
            )
            response = json.loads(response.get('Payload').read())
        except Exception as e:
            raise e
