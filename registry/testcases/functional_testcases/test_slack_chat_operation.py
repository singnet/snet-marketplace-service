import json
from datetime import datetime as dt
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import urlencode

from registry.application.handlers.slack_chat_operation_handler import get_list_of_service_pending_for_approval
from registry.application.handlers.slack_chat_operation_handler import slack_interaction_handler
from registry.constants import OrganizationStatus, ServiceStatus, OrganizationAddressType, OrganizationType
from registry.domain.models.organization import Organization as OrganizationDomainModel
from registry.infrastructure.models import Organization as OrganizationDBModel
from registry.infrastructure.models import OrganizationAddress as OrganizationAddressDBModel
from registry.infrastructure.models import OrganizationState as OrganizationStateDBModel
from registry.infrastructure.models import Service as ServiceDBModel
from registry.infrastructure.models import ServiceComment as ServiceCommentDBModel
from registry.infrastructure.models import ServiceState as ServiceStateDBModel
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

org_repo = OrganizationPublisherRepository()
service_repo = ServicePublisherRepository()


class TestSlackChatOperation(TestCase):
    def setUp(self):
        pass

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    @patch("registry.application.services.slack_chat_operation.requests.post")
    def test_get_list_of_service_pending_for_approval(self, post_request, validate_slack_signature,
                                                      validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
        post_request.return_value.status_code = 200
        post_request.return_value.text = ""
        self.tearDown()
        org_repo.add_organization(
            OrganizationDomainModel(
                "test_org_uuid", "test_org_id", "org_dummy", OrganizationType.ORGANIZATION.value, "PUBLISHER", "description",
                "short_description", "https://test.io", [], {}, "ipfs_hash", "123456879", [], [], [], []),
            "dummy", OrganizationStatus.PUBLISHED.value
        )
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid_1",
                display_name="test_display_name_1",
                service_id="test_service_id_1",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid_2",
                display_name="test_display_name_2",
                service_id="test_service_id_2",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1000,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid_1",
                state=ServiceStatus.APPROVAL_PENDING.value,
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1001,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid_2",
                state=ServiceStatus.APPROVAL_PENDING.value,
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        event = {
            "resource": "/services",
            "path": "/services",
            "httpMethod": "POST",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "mu1l28rgji.execute-api.us-east-1.amazonaws.com",
                "X-Slack-Request-Timestamp": "1585592248",
                "X-Slack-Signature": "v0=2f1e3b11bd3758d159971da4f0c2fe4569757a5ebb7991a48f84ee19cbfd7725"
            },
            "queryStringParameters": None,
            "requestContext": {},
            "body": urlencode({"token": "HiVKf04RB8GV6bmaaBqx7nAr", "team_id": "T996H7VS8", "team_domain": "snet",
                               "channel_id": "2QWW3E4R5RT6", "channel_name": "privategroup", "user_id": "UE8CNNEGZ",
                               "user_name": "dummy", "command": "/list-orgs-for-approval",
                               "response_url": "https://hooks.slack.com/commands",
                               "trigger_id": "1026304454913.315221267892.794872083bae86aa00c776ba3bc74b30"}
                              ),
            "isBase64Encoded": False
        }
        response = get_list_of_service_pending_for_approval(event, context=None)
        assert (response["statusCode"] == 200)

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    @patch("registry.application.services.slack_chat_operation.requests.post")
    @patch("common.utils.send_email_notification")
    def test_slack_interaction_handler_to_view_service_modal(
            self, email_notification, post_request, validate_slack_signature,
            validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
        post_request.return_value.status_code = 200
        self.tearDown()
        org_repo.add_organization(
            OrganizationDomainModel(
                "test_org_uuid", "test_org_id", "org_dummy", OrganizationType.ORGANIZATION.value, "PUBLISHER", "description",
                "short_description", "https://test.io", [], {}, "ipfs_hash", "123456879", [], [], [], []),
            "dummy", OrganizationStatus.PUBLISHED.value)
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid_1",
                display_name="test_display_name_1",
                service_id="test_service_id_1",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1000,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid_1",
                state=ServiceStatus.APPROVAL_PENDING.value,
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        event = {"resource": "/submit",
                 "path": "/submit",
                 "httpMethod": "POST",
                 "headers": {"Accept": "application/json,*/*",
                             "Content-Type": "application/x-www-form-urlencoded",
                             "X-Slack-Request-Timestamp": "1585742597",
                             "X-Slack-Signature": "v0=5096314f4b78b0b75366d8429a5195ea01c7e67f5618ee05f8e94a94953e05fd"},
                 "body": urlencode(
                     {
                         "payload": json.dumps(
                             {
                                 "type": "block_actions", "team": {"id": "T996H7VS8", "domain": "snet"},
                                 "user": {"username": "dummy"},
                                 "trigger_id": "1028338009186.315221267892.83550c5f247eb73b0ad743511e8698a6",
                                 "channel": {"id": "Q2W3E4R5T6"},
                                 "response_url": "https://hooks.slack.com/actions",
                                 "actions": [
                                     {"action_id": "review", "block_id": "NJ0wG",
                                      "text": {"type": "plain_text", "text": "Review",
                                               "emoji": True},
                                      "value": json.dumps(
                                          {"org_id": "test_org_id",
                                           "service_id": "test_service_id_1",
                                           "path": "/service"}
                                      ),
                                      "style": "primary", "type": "button",
                                      "action_ts": "1585742597.398302"
                                      }
                                 ]
                             }
                         )
                     }
                 ),
                 "isBase64Encoded": False}
        response = slack_interaction_handler(event=event, context=None)
        assert (response["statusCode"] == 200)

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    @patch("common.utils.send_email_notification")
    def test_review_submission_for_service(self, email_notification, validate_slack_signature,
                                           validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
        self.tearDown()
        org_repo.add_organization(
            OrganizationDomainModel(
                "test_org_uuid", "test_org_id", "org_dummy", OrganizationType.ORGANIZATION.value, "PUBLISHER", "description",
                "short_description", "https://test.io", [], {}, "ipfs_hash", "123456879", [], [], [], []),
            "dummy", OrganizationStatus.PUBLISHED.value)
        service_repo.add_item(
            ServiceDBModel(
                org_uuid="test_org_uuid",
                uuid="test_service_uuid_1",
                display_name="test_display_name_1",
                service_id="test_service_id_1",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                created_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceStateDBModel(
                row_id=1000,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid_1",
                state=ServiceStatus.APPROVAL_PENDING.value,
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=dt.utcnow()
            )
        )
        event = {
            "resource": "/submit",
            "path": "/submit",
            "httpMethod": "POST",
            "headers": {"Accept": "application/json,*/*",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-Slack-Request-Timestamp": "1585737114",
                        "X-Slack-Signature": "v0=5f52fbfa5a80733a0c7d9cad29dc69b452c402ad314e3409202a7b58f478461d"},
            "body": urlencode({
                "payload": json.dumps(
                    {
                        "type": "view_submission",
                        "user": {"username": "dummy"},
                        "trigger_id": "1042957767015.315221267892.fc7b53b0ce0f2d82c63b75e8b8600718",
                        "view":
                            {
                                "type": "modal",
                                "blocks":
                                    [
                                        {
                                            "type": "section",
                                            "block_id": "7Jh",
                                            "fields": [
                                                {
                                                    "type": "mrkdwn", "text": "*Organization Id:*\ntest_org_id",
                                                    "verbatim": False
                                                },
                                                {
                                                    "type": "mrkdwn", "text": "*Service Id:*\ntest_service_id_1",
                                                    "verbatim": False
                                                },
                                                {
                                                    "type": "mrkdwn", "text": "*Service Name:*\ntest_display_name_1",
                                                    "verbatim": False
                                                },
                                                {
                                                    "type": "mrkdwn",
                                                    "text": "*Approval Platform:*\n<http://dummy.com>\n",
                                                    "verbatim": False
                                                },
                                                {"type": "mrkdwn",
                                                 "text": "*When:*\nMar10, 2020 (16 Days before)\n",
                                                 "verbatim": False
                                                 }
                                            ]
                                        }],
                                "state": {"values": {
                                    "approval_state": {"selection": {"type": "radio_buttons",
                                                                     "selected_option": {
                                                                         "text": {"type": "plain_text",
                                                                                  "text": "Reject",
                                                                                  "emoji": True},
                                                                         "value": "REJECTED",
                                                                         "description": {
                                                                             "type": "plain_text",
                                                                             "text": "Description for option 2",
                                                                             "emoji": True}}}},
                                    "review_comment": {"comment": {"type": "plain_text_input",
                                                                   "value": "service has missing proto files"}}}},
                                "title": {
                                    "type": "plain_text", "text": "Service For Approval",
                                    "emoji": True}},
                        "response_urls": []}
                )
            }
            ),
            "isBase64Encoded": False
        }
        response = slack_interaction_handler(event=event, context=None)
        assert (response["statusCode"] == 200)

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_review_submission_for_organization(
            self, lambda_response, validate_slack_signature, validate_slack_channel_id,  validate_slack_user):
        validate_slack_user.return_value = True
        validate_slack_channel_id.return_value = True
        validate_slack_signature.return_value = True
        lambda_response.return_value = {"StatusCode": 202}
        self.tearDown()
        org_repo.add_organization(
            OrganizationDomainModel(
                "test_org_uuid", "test_org_id", "org_dummy", OrganizationType.ORGANIZATION.value, "PUBLISHER", "description",
                "short_description", "https://test.io", [], {}, "ipfs_hash", "123456879", [], [], [], []),
            "dummy", OrganizationStatus.ONBOARDING.value)
        event = {
            "resource": "/slack/interaction/submit",
            "path": "/slack-approval/slack/interaction/submit",
            "httpMethod": "POST",
            "headers": {
                "X-Slack-Request-Timestamp": "1586262180",
                "X-Slack-Signature": "v0=3870786bc3c7d03367eb0fa81c2421fbed855f8afafe7f7a5e294d75d592961e"
            },
            "body": urlencode({
                "payload": json.dumps({
                    "type": "view_submission",
                    "team": {"id": "T996H7VS8", "domain": "snet"},
                    "user": {"username": "dummy"},
                    "trigger_id": "1045596158583.315221267892.fa50212a87f6c7cd28234be6512803b1",
                    "view": {
                        "type": "modal",
                        "blocks": [
                            {
                                "fields": [
                                    {"type": "mrkdwn", "text": "*Organization Id:*\ntest_org_id"},
                                    {"type": "mrkdwn", "text": "*Organization Name:*\nTest Organization"},
                                    {"type": "mrkdwn",
                                     "text": "*Approval Platform:*\n<http://staging-dapp.singularitynet.io.s3-website-us-east-1.amazonaws.com/servicedetails/servicedetails/org/test_org_id>\n"}
                                ]
                            },
                            {
                                "type": "section", "block_id": "/jQ",
                                "text": {"type": "mrkdwn", "text": "*Comments*\n*No comment"}},
                            {
                                "type": "input", "block_id": "approval_state",
                                "label": {"type": "plain_text",
                                          "text": "*Approve / Reject / Request Change*",
                                          "emoji": True
                                          },
                                "optional": False
                            },
                            {
                                "type": "input", "block_id": "review_comment",
                                "label": {"type": "plain_text", "text": "Comment",
                                          "emoji": True},
                                "hint": {"type": "plain_text",
                                         "text": "* Comment is mandatory field.",
                                         "emoji": True},
                                "optional": False
                            }
                        ],
                        "state": {
                            "values": {
                                "approval_state": {
                                    "selection": {
                                        "type": "radio_buttons",
                                        "selected_option": {
                                            "text": {
                                                "type": "plain_text",
                                                "text": "Approve",
                                                "emoji": True
                                            },
                                            "value": "APPROVED",
                                            "description": {
                                                "type": "plain_text",
                                                "text": "Allow user to publish organization.",
                                                "emoji": True
                                            }
                                        }
                                    }
                                },
                                "review_comment": {
                                    "comment": {
                                        "type": "plain_text_input",
                                        "value": "1234"
                                    }
                                }
                            }
                        },
                        "title": {
                            "type": "plain_text",
                            "text": "Org For Approval",
                            "emoji": True
                        },
                        "clear_on_close": False,
                        "notify_on_close": False,
                        "close": {
                            "type": "plain_text", "text": "Cancel", "emoji": True
                        },
                        "submit": {
                            "type": "plain_text", "text": "Submit", "emoji": True
                        }
                    },
                    "response_urls": []})
            }),"isBase64Encoded": False
        }
        response = slack_interaction_handler(event=event, context=None)
        assert (response["statusCode"] == 200)

    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_user")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_channel_id")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.validate_slack_signature")
    @patch("registry.application.services.slack_chat_operation.requests.post")
    @patch("registry.application.services.slack_chat_operation.SlackChatOperation.get_verification_latest_comments")
    def test_slack_interaction_handler_to_view_org_modal(
            self, verification_latest_comments, post_request, validate_slack_signature,
            validate_slack_channel_id, validate_slack_user):
        validate_slack_channel_id.return_value = True
        validate_slack_user.return_value = True
        validate_slack_signature.return_value = True
        verification_latest_comments.return_value = None
        post_request.return_value.status_code = 200
        self.tearDown()
        org_repo.add_organization(
            OrganizationDomainModel(
                "test_org_uuid", "test_org_id", "org_dummy", OrganizationType.ORGANIZATION.value, "PUBLISHER", "description",
                "short_description", "https://test.io", [], {}, "ipfs_hash", "123456879", [], [], [], []),
            "dummy", OrganizationStatus.PUBLISHED.value)
        org_repo.add_item(
            OrganizationAddressDBModel(
                org_uuid="test_org_uuid",
                address_type=OrganizationAddressType.HEAD_QUARTER_ADDRESS.value,
                street_address="Dummy Street",
                apartment="Dummy Apartment",
                city="Dummy City",
                pincode="000000",
                state="Dummy State",
                country="Dummy Country",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {"resource": "/submit",
                 "path": "/submit",
                 "httpMethod": "POST",
                 "headers": {"Accept": "application/json,*/*",
                             "Content-Type": "application/x-www-form-urlencoded",
                             "X-Slack-Request-Timestamp": "1585742597",
                             "X-Slack-Signature": "v0=5096314f4b78b0b75366d8429a5195ea01c7e67f5618ee05f8e94a94953e05fd"},
                 "body": urlencode(
                     {
                         "payload": json.dumps(
                             {
                                 "type": "block_actions", "team": {"id": "T996H7VS8", "domain": "snet"},
                                 "user": {"username": "dummy"},
                                 "trigger_id": "1028338009186.315221267892.83550c5f247eb73b0ad743511e8698a6",
                                 "channel": {"id": "Q2W3E4R5T6"},
                                 "response_url": "https://hooks.slack.com/actions",
                                 "actions": [
                                     {"action_id": "review", "block_id": "NJ0wG",
                                      "text": {"type": "plain_text", "text": "Review",
                                               "emoji": True},
                                      "value": json.dumps(
                                          {"org_id": "test_org_id",
                                           "path": "/org"}
                                      ),
                                      "style": "primary", "type": "button",
                                      "action_ts": "1585742597.398302"
                                      }
                                 ]
                             }
                         )
                     }
                 ),
                 "isBase64Encoded": False}
        response = slack_interaction_handler(event=event, context=None)
        assert (response["statusCode"] == 200)

    def tearDown(self):
        org_repo.session.query(OrganizationDBModel).delete()
        org_repo.session.query(OrganizationStateDBModel).delete()
        org_repo.session.query(ServiceDBModel).delete()
        org_repo.session.query(ServiceStateDBModel).delete()
        org_repo.session.query(ServiceCommentDBModel).delete()
