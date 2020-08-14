import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import uuid4

from verification.application.handlers.slack_handlers import get_pending_individual_verification, slack_interaction_handler
from verification.application.services.slack_operation import individual_repository
from verification.constants import IndividualVerificationStatus
from verification.infrastructure.models import IndividualVerificationModel


@patch("verification.application.services.slack_operation.requests.post")
class TestSlackOperation(TestCase):
    def test_get_list_of_service_pending_for_approval(self, post_request):
        post_request.return_value.status_code = 200
        verification_id = uuid4().hex
        individual_username = "user@dummy.io"
        reviewer = "dummy.dummy"
        channel_id = "dummy_channel_id"
        current_time = datetime.now()
        individual_repository.add_item(IndividualVerificationModel(verification_id=verification_id, username=individual_username, comments=[], status=IndividualVerificationStatus.PENDING.value, created_at=current_time, updated_at=current_time))
        event = {
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "mu1l28rgji.execute-api.us-east-1.amazonaws.com",
                "X-Slack-Request-Timestamp": "1585592248",
                "X-Slack-Signature": "v0=9a2ea23fc8e35f5e67a4318ef3915e4157ae101842c4d713d97f6bdb3b7a4c6f"
            },
            "body": urlencode({
                "team_id": "1234",
                "team_domain": "dummy",
                "channel_id": channel_id,
                "channel_name": "private-channel",
                "user_id": "dummy123",
                "user_name": reviewer,
                "response_url": "https://hooks.slack.com/commands",
                "trigger_id": "1"
            })
        }
        response = get_pending_individual_verification(event, None)
        self.assertEqual(response["statusCode"], 200)

    def test_review_individual(self, post_request):
        verification_id = uuid4().hex
        reviewer = "dummy.dummy"
        individual_username = "user@dummy.io"
        channel_id = "dummy_channel_id"
        current_time = datetime.now()
        individual_repository.add_item(IndividualVerificationModel(verification_id=verification_id, username=individual_username, comments=[], status=IndividualVerificationStatus.PENDING.value, created_at=current_time, updated_at=current_time))
        event = {
            "headers": {
                "X-Slack-Request-Timestamp": "1586262180",
                "X-Slack-Signature": 'v0=48523e240e017d13467c98a3c28611835aeabc14f071f5888748b06f01837bf8'
            },
            "body": urlencode({
                "payload": json.dumps({
                    "type": "block_actions", "team": {"id": "1234", "domain": "dummy"},
                    "user": {"username": reviewer},
                    "trigger_id": "123",
                    "channel": {"id": channel_id},
                    "response_url": "https://hooks.slack.com/actions",
                    "actions": [
                        {"action_id": "review", "block_id": "NJ0wG",
                         "text": {"type": "plain_text", "text": "Review",
                                  "emoji": True},
                         "value": json.dumps(
                             {"username": individual_username}
                         ),
                         "style": "primary", "type": "button",
                         "action_ts": "1585742597.398302"
                         }
                    ]
                })
            })
        }
        response = slack_interaction_handler(event, None)
        self.assertEqual(response["statusCode"], 200)

    def tearDown(self):
        individual_repository.session.query(IndividualVerificationModel).delete()
        individual_repository.session.commit()
