import json

import requests

from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import validate_signature
from verification.application.services.verification_manager import individual_repository, VerificationManager
from verification.config import ALLOWED_SLACK_USER, SIGNING_SECRET, ALLOWED_SLACK_CHANNEL_ID, \
    SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, MAX_INDIVIDUAL_SLACK_LISTING, SLACK_APPROVAL_CHANNEL_URL
from verification.constants import IndividualVerificationStatus, OPEN_SLACK_VIEW_URL
from verification.exceptions import InvalidSlackUserException, InvalidSlackChannelException, \
    InvalidSlackSignatureException

logger = get_logger(__name__)


class SlackOperation:
    def __init__(self, username, channel_id):
        self._username = username
        self._channel_id = channel_id

    @staticmethod
    def generate_slack_signature_message(request_timestamp, event_body):
        message = f"v0:{request_timestamp}:{event_body}"
        return message

    @staticmethod
    def validate_slack_signature(signature, message):
        return validate_signature(signature=signature, message=message, key=SIGNING_SECRET,
                                  opt_params={"slack_signature_prefix": "v0="})

    def validate_slack_user(self):
        if self._username in ALLOWED_SLACK_USER:
            return True
        return False

    def validate_slack_channel_id(self):
        if self._channel_id in ALLOWED_SLACK_CHANNEL_ID:
            return True
        return False

    def validate_slack_request(self, headers, payload_raw, ignore=False):
        if not ignore:
            if not self.validate_slack_channel_id():
                raise InvalidSlackChannelException()

        if not self.validate_slack_user():
            raise InvalidSlackUserException()

        slack_signature_message = self.generate_slack_signature_message(
            request_timestamp=headers["X-Slack-Request-Timestamp"], event_body=payload_raw)

        if not self.validate_slack_signature(
                signature=headers["X-Slack-Signature"], message=slack_signature_message):
            raise InvalidSlackSignatureException()

    def get_pending_individual_verification(self):
        individual_verification_list = VerificationManager().get_pending_individual_verification(limit=MAX_INDIVIDUAL_SLACK_LISTING)
        slack_blocks = self.generate_slack_listing_blocks(individual_verification_list)
        slack_payload = {"blocks": slack_blocks}
        response = requests.post(url=SLACK_APPROVAL_CHANNEL_URL, data=json.dumps(slack_payload))
        logger.info(f"{response.status_code} | {response.text}")

    def process_interaction(self, payload):
        data = {}
        if payload["type"] == "block_actions":
            for action in payload["actions"]:
                if "button" == action.get("type"):
                    data = json.loads(action.get("value", {}))
                if not data:
                    raise BadRequestException()
                individual_username = data["username"]
                self.create_and_send_view_individual_modal(individual_username, payload["trigger_id"])
        elif payload["type"] == "view_submission":
            individual_username = payload["view"]["blocks"][0]["fields"][1]["text"]
            comment = payload["view"]["state"]["values"]["review_comment"]["comment"]["value"]
            review_request_state = \
                payload["view"]["state"]["values"]["approval_state"]["selection"]["selected_option"]["value"]
            self.process_approval_comment(review_request_state, comment, individual_username)

    def create_and_send_view_individual_modal(self, username, trigger_id):
        verification = individual_repository.get_verification(username=username)
        if verification is None:
            raise Exception(f"No verification found with username: {username}")
        comments = verification.comment_dict_list()
        comment = "No comment"
        comment_by = "-"
        if len(comments) > 0:
            comment = comments[0]["comment"]
            comment_by = comments[0]["created_by"]
        view = self.generate_view_individual_modal(username, comment, comment_by)
        slack_payload = {
            "trigger_id": trigger_id,
            "view": view
        }

        headers = {"Authorization": SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, "content-type": "application/json"}
        response = requests.post(url=OPEN_SLACK_VIEW_URL, data=json.dumps(slack_payload), headers=headers)
        logger.info(f"{response.status_code} | {response.text}")

    def process_approval_comment(self, state, comment, individual_username):
        verification = individual_repository.get_verification(username=individual_username)
        if verification.status in [IndividualVerificationStatus.PENDING.value,
                                   IndividualVerificationStatus.REJECTED.value,
                                   IndividualVerificationStatus.CHANGE_REQUESTED.value]:
            VerificationManager().callback(
                json.dumps({"verificationStatus": state, "comment": comment, "reviewed_by": self._username}),
                entity_id=individual_username)
        else:
            logger.info("Approval type is not valid")

    def generate_view_individual_modal(self, individual_username, comment, comment_by):
        view = {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Individual for Approval",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            }
        }
        info_display_block = {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Username:*"
                },
                {
                    "type": "plain_text",
                    "text": f"{individual_username}"
                },
            ]
        }
        approver_comment_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Comments*\n{comment}\n *Comment by*: {comment_by}"
            }
        }
        divider_block = {
            'type': 'divider'
        }
        select_approval_state_block = {
            "type": "input",
            "block_id": "approval_state",
            "element": {
                "type": "radio_buttons",
                "action_id": "selection",
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "Request Change"
                    },
                    "value": IndividualVerificationStatus.CHANGE_REQUESTED.value,
                    "description": {
                        "type": "plain_text",
                        "text": "Request changes."
                    }
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Approve"
                        },
                        "value": IndividualVerificationStatus.APPROVED.value,
                        "description": {
                            "type": "plain_text",
                            "text": "Allow user to publish service."
                        }
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Reject"
                        },
                        "value": IndividualVerificationStatus.REJECTED.value,
                        "description": {
                            "type": "plain_text",
                            "text": "Reject user request."
                        }
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Request Change"
                        },
                        "value": IndividualVerificationStatus.CHANGE_REQUESTED.value,
                        "description": {
                            "type": "plain_text",
                            "text": "Request changes."
                        }
                    }
                ]
            },
            "label": {
                "type": "plain_text",
                "text": "*Approve / Reject / Request Change*"
            }
        }
        comment_block = {
            "type": "input",
            "block_id": "review_comment",
            "optional": False,
            "element": {
                "type": "plain_text_input",
                "action_id": "comment",
                "multiline": True
            },
            "label": {
                "type": "plain_text",
                "text": "Comment",
                "emoji": True
            },
            "hint": {
                "type": "plain_text",
                "text": "* Comment is mandatory field."
            }
        }
        view["blocks"] = [info_display_block, divider_block, approver_comment_block,
                          select_approval_state_block, comment_block]
        return view

    def generate_slack_listing_blocks(self, verifications):
        title_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Individual Verification Requests*"
            }
        }
        listing_slack_blocks = [title_block]
        for verification in verifications:
            individual_username = verification["username"]
            mrkdwn_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Username:* {individual_username}"
                    }
                ]
            }
            review_button_block = {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Review"
                        },
                        "style": "primary",
                        "value": json.dumps({
                            "username": individual_username
                        })
                    }
                ]
            }
            divider_block = {
                "type": "divider"
            }
            listing_slack_blocks.extend([mrkdwn_block, review_button_block, divider_block])
        return listing_slack_blocks
