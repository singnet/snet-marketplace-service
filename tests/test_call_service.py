import json
import unittest
from stub import example_service_pb2
from unittest.mock import patch

import lambda_handler


class TestSignUPAPI(unittest.TestCase):
    def setUp(self):
        self.event = {"requestContext": {"stage": "TEST"}}

        self.call_service = {"path": "/call-service",
                             "httpMethod": "POST",
                             "body": {"user_address": "12345", "org_id": "snet", "service_id": "example-service",
                                      "method": "add", "input": str(example_service_pb2.Numbers(a=3, b=5))
                                      }
                             }

    @patch('common.utils.Utils.report_slack')
    def test_request_handler(self, mock_get):
        # event dict is {}
        response = lambda_handler.request_handler(event=self.event, context=None)
        assert (response["statusCode"] == 400)
        assert (response["body"] == '"Bad Request"')

        # event dict has invalid path
        test_event = {"path": "/dummy", "httpMethod": "GET"}
        test_event.update(self.event)
        response = lambda_handler.request_handler(event=test_event, context=None)
        assert (response["statusCode"] == 400)
        assert (response["body"] == '"Invalid URL path."')

    @patch('client.Client.call_service')
    def test_call_service(self, mock_get):
        self.call_service.update(self.event)
        self.call_service['body'] = json.dumps(self.call_service['body'])
        mock_get.return_value = {'status': 'StatusCode.OK'}
        response = lambda_handler.request_handler(event=self.call_service, context=None)
        assert(response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert(response_body["data"]['status'] == 'StatusCode.OK')


if __name__ == '__main__':
    unittest.main()
