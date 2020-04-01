import json

import requests

from common.logger import get_logger
from common.utils import validate_signature
from registry.application.services.organization_publisher_service import OrganizationPublisherService
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.config import SIGNING_SECRET
from registry.config import STAGING_URL, ALLOWED_SLACK_USER, SLACK_APPROVAL_CHANNEL_URL, \
    ALLOWED_SLACK_CHANNEL_ID, MAX_SERVICES_SLACK_LISTING
from registry.exceptions import InvalidSlackChannelException, InvalidSlackUserException, InvalidSlackSignatureException

logger = get_logger(__name__)


class SlackChatOperation:
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

    def validate_slack_request(self, headers, payload_raw):
        if not self.validate_slack_channel_id():
            raise InvalidSlackChannelException()

        if not self.validate_slack_user():
            raise InvalidSlackUserException()

        slack_signature_message = self.generate_slack_signature_message(
            request_timestamp=headers["X-Slack-Request-Timestamp"], event_body=payload_raw)

        if not self.validate_slack_signature(
                signature=headers["X-Slack-Signature"], message=slack_signature_message):
            raise InvalidSlackSignatureException()

    def validate_slack_user(self):
        if self._username in ALLOWED_SLACK_USER:
            return True
        return False

    def validate_slack_channel_id(self):
        if self._channel_id in ALLOWED_SLACK_CHANNEL_ID:
            return True
        return False

    def get_list_of_service_pending_for_approval(self):
        list_of_service_pending_for_approval = \
            ServicePublisherService(username=None, org_uuid=None, service_uuid=None). \
                get_list_of_service_pending_for_approval(limit=MAX_SERVICES_SLACK_LISTING)
        slack_blocks = self.generate_service_listing_slack_blocks(list_of_service_pending_for_approval)
        slack_payload = {"blocks": slack_blocks}
        logger.info(f"slack_payload: {slack_payload}")
        response = requests.post(url=SLACK_APPROVAL_CHANNEL_URL, data=json.dumps(slack_payload))
        logger.info(f"{response.status_code} | {response.text}")
        return ""

    def get_list_of_organizations_pending_for_approval(self):
        organization_list = OrganizationPublisherService(None, None)\
            .get_approval_pending_organizations(MAX_SERVICES_SLACK_LISTING)
        slack_blocks = self.generate_organization_listing_slack_blocks(organization_list)
        slack_payload = {"blocks": slack_blocks}
        logger.info(f"slack_payload: {slack_payload}")
        response = requests.post(url=SLACK_APPROVAL_CHANNEL_URL, data=json.dumps(slack_payload))
        logger.info(f"{response.status_code} | {response.text}")
        return ""

    def generate_organization_listing_slack_blocks(self, organizations):
        pass

    def generate_service_listing_slack_blocks(self, services):
        title_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Service Approval Request*"
            }
        }
        service_listing_slack_blocks = [title_block]
        for service_dict in services:
            mrkdwn_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Service Id:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Requested on:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"<{STAGING_URL}|{service_dict['service_id']}>"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{service_dict['requested_at']}"
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
                        # "value": f"{SERVICE_REVIEW_API_ENDPOINT}?org_uuid={service_dict['org_uuid']}&service_uuid={service_dict['service_uuid']}"
                        "value": "https:google.com"
                    }
                ]
            }
            divider_block = {
                "type": "divider"
            }
            service_listing_slack_blocks = service_listing_slack_blocks + [mrkdwn_block, review_button_block,
                                                                           divider_block]
        return service_listing_slack_blocks
