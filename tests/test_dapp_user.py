import json
import unittest
from unittest.mock import patch

from dapp_user import lambda_handler


class TestDappUserAPI(unittest.TestCase):
    def setUp(self):
        self.event = {"requestContext": {"stage": "TEST"}}

        self.signup = {"path": "/signup",
                       "httpMethod": "GET",
                       "requestContext":
                           {"authorizer":
                            {"claims":
                                     {"email_verified": True,
                                      "nickname": "Dummy",
                                      "email": "dummy@dummy.com"
                                      }
                             },
                            "accountId": "123456",
                            "requestId": "T01",
                            "requestTimeEpoch": "987654321"
                            }
                       }

        self.delete_user = {"path": "/delete-user",
                            "httpMethod": "GET",
                            "requestContext":
                                {"authorizer":
                                    {"claims":
                                     {"email": "dummy@dummy.com"}
                                     }
                                 }
                            }

        self.get_user_profile = {"path": "/profile",
                                 "httpMethod": "GET",
                                 "requestContext":
                                 {"authorizer":
                                  {"claims":
                                         {"email": "dummy@dummy.com"}
                                   }
                                  }
                                 }

        self.update_user_profile = {"path": "/profile",
                                    "httpMethod": "POST",
                                    "body": '{"email_alerts": true, "is_terms_accepted": true}',
                                    "requestContext":
                                        {"authorizer":
                                            {"claims":
                                             {"email": "dummy@dummy.com"}
                                             }
                                         }
                                    }
        self.get_user_feedback = {"path": "/feedback",
                                  "httpMethod": "GET",
                                  "queryStringParameters": {},
                                  "requestContext":
                                  {"authorizer":
                                   {"claims":
                                    {"email": "dummy@dummy.com"}
                                    }
                                   }
                                  }
        self.set_user_feedback = {"path": "/feedback",
                                  "httpMethod": "POST",
                                  "body": '{"feedback": {"org_id": "test-snet", "service_id": "test-service",'
                                          ' "user_rating": "4.0", "comment": "Good Job!"} }',
                                  "requestContext":
                                  {"authorizer":
                                   {"claims":
                                    {"email": "dummy@dummy.com"}
                                    }
                                   }
                                  }

    @patch('common.utils.Utils.report_slack')
    def test_request_handler(self, mock_get):
        # event dict is {}
        response = lambda_handler.request_handler(
            event=self.event, context=None)
        assert (response["statusCode"] == 400)
        assert (response["body"] == '"Bad Request"')

        # event dict has invalid path
        test_event = {"path": "/dummy", "httpMethod": "GET"}
        test_event.update(self.event)
        response = lambda_handler.request_handler(
            event=test_event, context=None)
        assert (response["statusCode"] == 404)
        assert (response["body"] == '"Not Found"')

    @patch('common.utils.Utils.report_slack')
    def test_user_signup(self, report_slack_mock):
        self.test_del_user_data()
        report_slack_mock.return_value = "mock_address"
        self.signup['requestContext'].update(self.event['requestContext'])
        response = lambda_handler.request_handler(
            event=self.signup, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        # hit again with same payload
        response = lambda_handler.request_handler(
            event=self.signup, context=None)
        assert (response["statusCode"] == 500)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "failed")

    def test_del_user_data(self):
        self.delete_user['requestContext'].update(self.event['requestContext'])
        response = lambda_handler.request_handler(
            event=self.delete_user, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_get_user_profile(self):
        self.get_user_profile['requestContext'].update(
            self.event['requestContext'])
        response = lambda_handler.request_handler(
            event=self.get_user_profile, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_update_user_profile(self):
        self.update_user_profile['requestContext'].update(
            self.event['requestContext'])
        response = lambda_handler.request_handler(
            event=self.update_user_profile, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_get_user_feedback(self):
        self.get_user_feedback['requestContext'].update(
            self.event['requestContext'])
        response = lambda_handler.request_handler(
            event=self.get_user_feedback, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_set_user_feedback(self):
        self.set_user_feedback['requestContext'].update(
            self.event['requestContext'])
        response = lambda_handler.request_handler(
            event=self.set_user_feedback, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")


if __name__ == '__main__':
    unittest.main()
