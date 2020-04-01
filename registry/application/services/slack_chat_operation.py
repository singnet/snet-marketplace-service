import json
import requests
from common.utils import validate_signature
from common.logger import get_logger
from registry.config import SIGNING_SECRET, SLACK_APPROVAL_OAUTH_ACCESS_TOKEN
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.config import STAGING_URL, ALLOWED_SLACK_USER, SERVICE_REVIEW_API_ENDPOINT, SLACK_APPROVAL_CHANNEL_URL, \
    ALLOWED_SLACK_CHANNEL_ID, MAX_SERVICES_SLACK_LISTING
from registry.domain.models.service_comment import ServiceComment
from registry.domain.models.service_state import ServiceState
from registry.constants import UserType, ServiceSupportType, ServiceStatus

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
            org_id = service_dict["org_id"]
            service_id = service_dict["service_id"]
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
                        "text": f"<{STAGING_URL}/servicedetails/org/{org_id}/service/{service_id}|{service_id}>"
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
                        "value": f"'service_id':{service_id},'org_id':{org_id},'path':'/service'"
                    }
                ]
            }
            divider_block = {
                "type": "divider"
            }
            service_listing_slack_blocks = service_listing_slack_blocks + [mrkdwn_block, review_button_block,
                                                                           divider_block]
        return service_listing_slack_blocks

    def process_approval_comment(self, approval_type, state, comment, params):
        if approval_type == "organization":
            pass
        elif approval_type == "service":
            org_uuid, service = ServicePublisherRepository(). \
                get_service_for_given_service_id_and_org_id(org_id=params["org_id"], service_id=params["service_id"])
            if service.service_state.state == ServiceStatus.APPROVAL_PENDING.value:
                ServicePublisherRepository().save_service(username=self._username, service=service,
                                                          state=getattr(ServiceStatus, state).value)
                service_comments = ServiceComment(
                    org_uuid=service.org_uuid,
                    service_uuid=service.uuid,
                    support_type=ServiceSupportType.SERVICE_APPROVAL.value,
                    user_type=UserType.SERVICE_APPROVER.value,
                    commented_by=self._username,
                    comment=comment
                )
                ServicePublisherRepository().save_service_comments(service_comment=service_comments)
                logger.info(f"Reviews for service with {service.service_id} is successfully submitted.")
            else:
                logger.info("Service state is not valid.")

    def create_and_send_view_service_modal(self, org_id, service_id, trigger_id):
        org_uuid, service = ServicePublisherRepository(). \
            get_service_for_given_service_id_and_org_id(org_id=org_id, service_id=service_id)
        view = self.generate_view_service_modal(org_id, service, None)
        slack_payload = {
            "trigger_id": trigger_id,
            "view": view
        }
        OPEN_SLACK_VIEW_URL = "https://slack.com/api/views.open"
        headers = {"Authorization": SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, "content-type": "application/json"}
        logger.info(f"slack_payload: {slack_payload}")
        response = requests.post(url=OPEN_SLACK_VIEW_URL, data=json.dumps(slack_payload), headers=headers)
        logger.info(f"{response.status_code} | {response.text}")

    def generate_view_service_modal(self, org_id, service, requested_at):
        view = {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Service For Approval",
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
        blocks = []
        service_info_display_block = {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Organization Id:*\n{org_id}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Service Id:*\n{service.service_id}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Service Name:*\n{service.display_name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Approval Platform:*\n{STAGING_URL}/servicedetails/org/{org_id}/service/{service.service_id}\n"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*When:*\n{requested_at}\n"
                }
            ]
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
                    "value": ServiceStatus.CHANGE_REQUESTED.value,
                    "description": {
                        "type": "plain_text",
                        "text": "Description for option 3"
                    }
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Approve"
                        },
                        "value": ServiceStatus.APPROVED.value,
                        "description": {
                            "type": "plain_text",
                            "text": "Description for option 1"
                        }
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Reject"
                        },
                        "value": ServiceStatus.REJECTED.value,
                        "description": {
                            "type": "plain_text",
                            "text": "Description for option 2"
                        }
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Request Change"
                        },
                        "value": ServiceStatus.CHANGE_REQUESTED.value,
                        "description": {
                            "type": "plain_text",
                            "text": "Description for option 3"
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
        blocks = [service_info_display_block, divider_block, select_approval_state_block, comment_block]
        view["blocks"] = blocks
        return view
