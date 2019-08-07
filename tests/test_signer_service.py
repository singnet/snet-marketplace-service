import json
import unittest
from unittest.mock import patch

import lambda_handler


class TestSignUPAPI(unittest.TestCase):
    def setUp(self):
        self.event = {"requestContext": {"stage": "TEST"}}

        self.signature_for_free_call = {"path": "/free-call",
                                        "httpMethod": "GET",
                                        "queryStringParameters": {"org_id": "test-org", "service_id": "test-service-id"},
                                        "requestContext":
                                            {"authorizer":
                                                 {"claims":
                                                      {"email": "dummy@dummy.com"}
                                                  }
                                             }
                                        }
        self.signature_for_regular_call = {"path": "/regular-call",
                                           "httpMethod": "GET",
                                           "queryStringParameters": {"org_id": "test-org",
                                                                     "service_id": "test-service-id"},
                                           "requestContext":
                                               {"authorizer":
                                                    {"claims":
                                                         {"email": "dummy@dummy.com"}
                                                     }
                                                }
                                           }

    @patch('common.utils.Utils.report_slack')
    def test_signature_for_free_call(self, report_slack_mock):
        self.signature_for_free_call['requestContext'].update(self.event['requestContext'])
        response = lambda_handler.request_handler(event=self.signature_for_free_call, context=None)
        print(response)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    # @patch('common.utils.Utils.report_slack')
    # def test_signature_for_regular_call(self, report_slack_mock):
    #     self.signature_for_regular_call['requestContext'].update(self.event['requestContext'])
    #     response = lambda_handler.request_handler(event=self.signature_for_regular_call, context=None)
    #     assert (response["statusCode"] == 200)
    #     response_body = json.loads(response["body"])
    #     assert (response_body["status"] == "success")