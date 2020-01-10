import json
from datetime import datetime
from unittest import TestCase

from common.repository import Repository
from dapp_user.application.handlers.user_handlers import add_or_update_user_preference, get_user_preference
from dapp_user.config import NETWORK_ID, NETWORKS
from dapp_user.constant import Status


class TestUserPreference(TestCase):
    def setUp(self):
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        username = "dummy_1@dummy.io"
        account_id = "123"
        name = "dummy_user_2"
        status = 1
        request_id = "id_123"
        user_one_row_id = 101
        current_time = datetime.utcnow()
        epoch_time = current_time.timestamp()
        self.repo.execute(
            "INSERT INTO user (row_id, username, account_id, name, email, email_verified, status, request_id, "
            "request_time_epoch, row_created, row_updated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [user_one_row_id, username, account_id, name, username, 1, status,
             request_id, epoch_time, current_time, current_time]
        )
        username = "dummy_2@dummy.io"
        account_id = "123"
        name = "dummy_user_2"
        status = 1
        user_two_row_id = 202
        request_id = "id_123"
        self.repo.execute(
            "INSERT INTO user (row_id, username, account_id, name, email, email_verified, status, request_id, "
            "request_time_epoch, row_created, row_updated) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [user_two_row_id, username, account_id, name, username, 1,
             status, request_id, epoch_time, current_time, current_time]
        )
        row_id = 1111
        user_row_id = user_two_row_id
        preference_type = "FEATURE_RELEASE"
        communication_type = "SMS"
        source = "PUBLISHER_DAPP"
        opt_out_reason = None
        status = 0
        self.repo.execute(
            "INSERT INTO user_preference(row_id, user_row_id, preference_type, communication_type, source, "
            "opt_out_reason, status, created_on, updated_on) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [row_id, user_row_id, preference_type, communication_type, source,
             opt_out_reason, status, current_time, current_time]
        )

    def test_add_or_update_user_preference(self):
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_1@dummy.io"
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
                        "email": "dummy_1@dummy.io"
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
                        "email": "dummy_1@dummy.io"
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

    def test_get_user_preference(self):
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_2@dummy.io"
                    }
                }
            }
        }
        response = get_user_preference(event=event, context=None)
        print(response)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"][0]["preference_type"] == "FEATURE_RELEASE")
        assert (response_body["data"][0]["communication_type"] == "SMS")
        assert (response_body["data"][0]["source"] == "PUBLISHER_DAPP")
        assert (response_body["data"][0]["status"] == 0)

    def tearDown(self):
        self.repo.execute("DELETE FROM user_preference")
        self.repo.execute("DELETE FROM user")
