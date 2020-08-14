import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock
from urllib.parse import urlencode
from uuid import uuid4

from verification.application.handlers.slack_handlers import get_pending_individual_verification, \
    slack_interaction_handler
from verification.application.services.slack_operation import individual_repository
from verification.constants import IndividualVerificationStatus, VerificationType, VerificationStatus
from verification.infrastructure.models import IndividualVerificationModel, VerificationModel


# @patch("verification.application.services.slack_operation.requests.post")
class TestSlackOperation(TestCase):
    def test_get_list_of_service_pending_for_approval(self, post_request):
        post_request.return_value.status_code = 200
        verification_id = uuid4().hex
        individual_username = "user@dummy.io"
        reviewer = "dummy.dummy"
        channel_id = "dummy_channel_id"
        current_time = datetime.now()
        individual_repository.add_item(
            IndividualVerificationModel(verification_id=verification_id, username=individual_username, comments=[],
                                        status=IndividualVerificationStatus.PENDING.value, created_at=current_time,
                                        updated_at=current_time))
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

    def test_review_individual(self):
        verification_id = uuid4().hex
        reviewer = "dummy.dummy"
        individual_username = "dummy@user.io"
        channel_id = "dummy_channel_id"
        current_time = datetime.now()
        individual_repository.add_item(
            IndividualVerificationModel(verification_id=verification_id, username=individual_username, comments=[],
                                        status=IndividualVerificationStatus.PENDING.value, created_at=current_time,
                                        updated_at=current_time))
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

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123"),
           invoke_lambda=Mock(return_value={"statusCode": 201})))
    def test_individual_review(self, mock_boto):
        verification_id = uuid4().hex
        reviewer = "dummy.dummy"
        individual_username = "dummy@user.io"
        current_time = datetime.now()
        individual_repository.add_all_items([
            IndividualVerificationModel(verification_id=verification_id, username=individual_username, comments=[],
                                        status=IndividualVerificationStatus.PENDING.value, created_at=current_time,
                                        updated_at=current_time),
            VerificationModel(id=verification_id, verification_type=VerificationType.INDIVIDUAL.value,
                              entity_id=individual_username, status=VerificationStatus.PENDING.value,
                              requestee=individual_username, reject_reason="",
                              created_at=current_time, updated_at=current_time)
        ])
        event = {
            'headers': {
                'X-Slack-Request-Timestamp': '1597392686',
                'X-Slack-Signature': 'v0=f2c25d50b954f887b9e6df1081746eddb2496a4a61f0c77402588bd9ab33cc41'
            },
            "body": urlencode({
                "payload": json.dumps({
                    "type": "view_submission",
                    "team": {"id": "1234", "domain": "dummy"},
                    "user": {
                        "id": "1234", "username": "dummy.dummy", "name": "dummy.dummy",
                        "team_id": "1234"},
                    "api_app_id": "1234",
                    "token": "1234",
                    "trigger_id": "1234",
                    "view": {"id": "1234", "team_id": "1234", "type": "modal",
                             "blocks": [
                                 {"type": "section", "block_id": "nHZc", "fields":
                                     [{"type": "mrkdwn", "text": "*Username:*", "verbatim": False},
                                      {"type": "plain_text", "text": individual_username, "emoji": True}]},
                                 {"type": "divider", "block_id": "Esi"},
                                 {"type": "section", "block_id": "1SdNK",
                                  "text": {"type": "mrkdwn",
                                           "text": "*Comments*\\nNo comment\\n *Comment by*: -", "verbatim": False}},
                                 {"type": "input", "block_id": "approval_state",
                                  "label": {"type": "plain_text",
                                            "text": "*Approve \\/ Reject \\/ Request Change*", "emoji": True},
                                  "optional": False,
                                  "element": {"type": "radio_buttons", "action_id": "selection",
                                              "initial_option":
                                                  {"text": {"type": "plain_text", "text": "Request Change",
                                                            "emoji": True},
                                                   "value": "CHANGE_REQUESTED",
                                                   "description":
                                                       {"type": "plain_text", "text": "Request changes.",
                                                        "emoji": True}},
                                              "options": [
                                                  {"text": {"type": "plain_text", "text": "Approve", "emoji": True},
                                                   "value": "APPROVED", "description": {"type": "plain_text",
                                                                                        "text": "Allow user to publish service.",
                                                                                        "emoji": True}},
                                                  {"text": {"type": "plain_text", "text": "Reject", "emoji": True},
                                                   "value": "REJECTED", "description": {"type": "plain_text",
                                                                                        "text": "Reject user request.",
                                                                                        "emoji": True}}, {
                                                      "text": {"type": "plain_text", "text": "Request Change",
                                                               "emoji": True}, "value": "CHANGE_REQUESTED",
                                                      "description": {"type": "plain_text",
                                                                      "text": "Request changes.",
                                                                      "emoji": True}}]}},
                                 {"type": "input", "block_id": "review_comment",
                                  "label": {"type": "plain_text", "text": "Comment", "emoji": True},
                                  "hint": {"type": "plain_text", "text": "* Comment is mandatory field.",
                                           "emoji": True},
                                  "optional": False,
                                  "element": {"type": "plain_text_input", "action_id": "comment", "multiline": True}}
                             ],
                             "state": {"values": {"approval_state": {"selection": {"type": "radio_buttons",
                                                                                   "selected_option": {
                                                                                       "text": {"type": "plain_text",
                                                                                                "text": "Request Change",
                                                                                                "emoji": True},
                                                                                       "value": "CHANGE_REQUESTED",
                                                                                       "description": {
                                                                                           "type": "plain_text",
                                                                                           "text": "Request changes.",
                                                                                           "emoji": True}}}},
                                                  "review_comment": {
                                                      "comment": {"type": "plain_text_input", "value": "change it"}}}},
                             "title": {"type": "plain_text", "text": "Individual for Approval", "emoji": True},
                             "clear_on_close": False,
                             "notify_on_close": False,
                             "close": {"type": "plain_text", "text": "Cancel", "emoji": True},
                             "submit": {"type": "plain_text", "text": "Submit", "emoji": True},
                             "previous_view_id": None
                             },
                    "response_urls": []})
            })
        }
        slack_interaction_handler(event, None)
        individual_verification = individual_repository.session.query(IndividualVerificationModel).filter(IndividualVerificationModel.verification_id == verification_id).all()
        if len(individual_verification) != 1:
            assert False
        self.assertEqual(individual_verification[0].status, IndividualVerificationStatus.CHANGE_REQUESTED.value)

    def tearDown(self):
        individual_repository.session.query(IndividualVerificationModel).delete()
        individual_repository.session.commit()
