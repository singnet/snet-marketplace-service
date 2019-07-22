import json
import unittest
from unittest.mock import patch

from contract_api import lambda_handler1 as lambda_handler


class TestContractAPI(unittest.TestCase):
    def setUp(self):
        self.event = {"requestContext": {"stage": "TEST"}}
        self.get_all_org = {"path": "/org", "httpMethod": "GET"}

        self.get_all_srvcs = {"path": "/service", "httpMethod": "POST",
                              "body": '{"filters": []}'}

        self.api_group_info = {"path": "/org/test-snet/service/tests/group",
                               "httpMethod": "GET",
                               "queryStringParameters": {"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE"}
                               }

        self.api_get_user_feedback = {"path": "/user/0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE/feedback",
                                      "httpMethod": "GET"
                                      }
        self.api_set_user_feedback = {"path": "/feedback",
                                      "httpMethod": "POST",
                                      "body": '{"feedback": {"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE", '
                                              '"org_id": "test-snet", "service_id": "tests", "user_rating": "3.0", '
                                              '"comment": "Good Work."}}'
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
        print(response)
        assert (response["statusCode"] == 404)
        assert (response["body"] == '"Not Found"')
        # event with invalid method
        test_event["httpMethod"] = "PUT"
        response = lambda_handler.request_handler(event=test_event, context=None)
        assert (response["statusCode"] == 405)
        assert (response["body"] == '"Method Not Allowed"')

    def test_get_all_org(self):
        self.get_all_org.update(self.event)
        response = lambda_handler.request_handler(event=self.get_all_org, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_get_all_srvcs(self):
        self.get_all_srvcs.update(self.event)
        response = lambda_handler.request_handler(event=self.get_all_srvcs, context=None)
        print(response)
        assert (response["statusCode"] == 200)

    def test_api_group_info(self):
        self.api_group_info.update(self.event)
        response = lambda_handler.request_handler(event=self.api_group_info, context=None)
        print(response)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)

    def test_api_get_user_feedback(self):
        self.api_get_user_feedback.update(self.event)
        response = lambda_handler.request_handler(event=self.api_get_user_feedback, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")