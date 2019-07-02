import json
import unittest
from unittest.mock import patch

import lambda_handler


class TestContractAPI(unittest.TestCase):
    def setUp(self):
        self.event = {"requestContext": {"stage": "TEST"}}
        self.get_all_srvcs = {"path": "/service", "httpMethod": "GET"}
        self.api_group_info = {"path": "/org/test-snet/service/tests/group",
                               "httpMethod": "GET",
                               "queryStringParameters": {"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE"}
                               }
        self.api_channels = {"path": "/channels",
                             "httpMethod": "POST",
                             "body": '{"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE",'
                                     ' "org_id": "test-snet", "service_id": "tests"}'
                             }
        self.api_get_user_feedback = {"path": "/user/0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE/feedback",
                                      "httpMethod": "GET"
                                      }
        self.api_set_user_feedback = {"path": "/feedback",
                                      "httpMethod": "POST",
                                      "body": '{"feedback": {"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE", '
                                              '"org_id": "test-snet", "service_id": "tests", "up_vote": false,'
                                              ' "down_vote": true, "comment": "Good Work.", "signature": ""}}'
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
        assert (response["statusCode"] == 400)
        assert (response["body"] == '"Invalid URL path."')
        # event with post query with invalid payload
        test_event = {"path": "/channels",
                      "httpMethod": "POST",
                      "body": '{"wrong_user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE", '
                              '"org_id": "test-snet", "service_id": "tests"}'
                      }
        test_event.update(self.event)
        response = lambda_handler.request_handler(event=test_event, context=None)
        assert (response["statusCode"] == 500)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "failed")

    def test_api_group_info(self):
        self.api_group_info.update(self.event)
        response = lambda_handler.request_handler(event=self.api_group_info, context=None)
        print(response)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)

    def test_api_channels(self):
        self.api_channels.update(self.event)
        response = lambda_handler.request_handler(event=self.api_channels, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)
        self.api_channels["body"] = '{"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE"}'
        response = lambda_handler.request_handler(event=self.api_channels, context=None)
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

    @patch('registry.Registry.is_valid_feedbk')
    def test_api_set_user_feedback(self, mock_get):
        self.api_set_user_feedback.update(self.event)
        mock_get.return_value = True
        response = lambda_handler.request_handler(event=self.api_set_user_feedback, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_contract_api(self):
        self.get_all_srvcs.update(self.event)
        response = lambda_handler.request_handler(event=self.get_all_srvcs, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")


if __name__ == '__main__':
    unittest.main()
