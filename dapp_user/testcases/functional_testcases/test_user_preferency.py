import json
import unittest
from unittest import TestCase
from dapp_user.application.handlers.user_handlers import add_or_update_user_preference
from dapp_user.constant import Status


class TestUserPreference(TestCase):
    def setUp(self):
        pass

    def test_add_or_update_user_preference(self):
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user@dummy.io"
                    }
                }
            },
            "body": json.dumps([{
                "preference_type": "FEATURE_RELEASE",
                "communication_type": "EMAIL",
                "source": "PUBLISHER_DAPP",
                "status": True
            }, {
                "preference_type": "WEEKLY_SUMMARY",
                "communication_type": "EMAIL",
                "source": "PUBLISHER_DAPP",
                "status": True
            }])
        }
        response = add_or_update_user_preference(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == [Status.ENABLED.value, Status.ENABLED.value])
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user@dummy.io"
                    }
                }
            },
            "body": json.dumps([{
                "preference_type": "FEATURE_RELEASE",
                "communication_type": "EMAIL",
                "source": "PUBLISHER_DAPP",
                "status": False,
                "opt_out_reason": "Mail too frequent!"
            }])
        }
        response = add_or_update_user_preference(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == [Status.DISABLED.value])
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user@dummy.io"
                    }
                }
            },
            "body": json.dumps([{
                "preference_type": "FEATURE_RELEASE",
                "communication_type": "EMAIL",
                "source": "PUBLISHER_DAPP",
                "status": True
            }, {
                "preference_type": "WEEKLY_SUMMARY",
                "communication_type": "EMAIL",
                "source": "PUBLISHER_DAPP",
                "status": False,
                "opt_out_reason": "Mail too frequent!"
            }])
        }
        response = add_or_update_user_preference(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == [Status.ENABLED.value, Status.DISABLED.value])


if __name__ == '__main__':
    unittest.main()
