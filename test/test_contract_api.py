import json
import unittest
from unittest.mock import patch

from contract_api import lambda_handler


class TestContractAPI(unittest.TestCase):
    def setUp(self):
        self.event = {"requestContext": {"stage": "TEST"}}
        self.api_get_curated_services = {"path": "/service",
                                         "httpMethod": "GET"
                                         }
        self.api_channels = {"path": "/channels",
                             "httpMethod": "GET",
                             "queryStringParameters": {"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE"}
                             }
        self.api_group_info = {"path": "/group-info",
                               "httpMethod": "GET",
                               "queryStringParameters": {"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE"}
                               }
        self.api_available_channels = {"path": "/available-channels",
                                       "httpMethod": "POST",
                                       "body": '{"user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE", "org_id": "test-snet", "service_id": "tests"}'
                                       }
        self.api_expired_channel_info = {"path": "/expired-channels",
                                         "httpMethod": "GET",
                                         "queryStringParameters": {
                                             "user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE"}
                                         }
        self.api_get_all_srvc_by_tag = {"path": "/tags/tag1",
                                        "httpMethod": "GET"
                                        }
        self.api_get_user_feedback = {"path": "/feedback",
                                      "httpMethod": "GET",
                                      "queryStringParameters": {
                                          "user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE"}

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
        assert (response["statusCode"] == "400")
        assert (response["body"] == '"Bad Request"')
        # event dict has invalid path
        test_event = {"path": "/dummy", "httpMethod": "GET"}
        test_event.update(self.event)
        response = lambda_handler.request_handler(event=test_event, context=None)
        print(response)
        assert (response["statusCode"] == 500)
        assert (response["body"] == '"Invalid URL path."')
        # event with post query with invalid payload
        test_event = {"path": "/available-channels",
                      "httpMethod": "POST",
                      "body": '{"wrong_user_address": "0xFF2a327ed1Ca40CE93F116C5d6646b56991c0ddE", '
                              '"org_id": "test-snet", "service_id": "tests"}'
                      }
        test_event.update(self.event)
        response = lambda_handler.request_handler(event=test_event, context=None)
        assert (response["statusCode"] == 500)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "failed")

    def test_api_get_curated_services(self):
        self.api_get_curated_services.update(self.event)
        response = lambda_handler.request_handler(event=self.api_get_curated_services, context=None)
        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)

    def test_api_channels(self):
        self.api_channels.update(self.event)
        response = lambda_handler.request_handler(event=self.api_channels, context=None)

        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)

    def test_api_group_info(self):
        self.api_group_info.update(self.event)
        response = lambda_handler.request_handler(event=self.api_group_info, context=None)

        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)

    def test_api_available_channels(self):
        self.api_available_channels.update(self.event)
        response = lambda_handler.request_handler(event=self.api_available_channels, context=None)

        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)

    @patch('contract_api.channel.Channel.get_latest_block_no')
    def test_api_expired_channel_info(self, mock_get):
        self.api_expired_channel_info.update(self.event)
        # mocked with high value for last block no to get expired channels
        mock_get.return_value = 1000000000000000000000000000000
        response = lambda_handler.request_handler(event=self.api_expired_channel_info, context=None)

        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (len(response_body["data"]) > 0)

    def test_api_get_all_srvc_by_tag(self):
        self.api_get_all_srvc_by_tag.update(self.event)
        response = lambda_handler.request_handler(event=self.api_get_all_srvc_by_tag, context=None)

        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_api_get_user_feedback(self):
        self.api_get_user_feedback.update(self.event)
        response = lambda_handler.request_handler(event=self.api_get_user_feedback, context=None)

        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    @patch('contract_api.service.Service.is_valid_feedbk')
    def test_api_set_user_feedback(self, mock_get):
        self.api_set_user_feedback.update(self.event)
        mock_get.return_value = True
        response = lambda_handler.request_handler(event=self.api_set_user_feedback, context=None)

        assert (response["statusCode"] == "200")
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")


if __name__ == '__main__':
    unittest.main()
