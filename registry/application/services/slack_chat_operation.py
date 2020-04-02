import json
from urllib.parse import parse_qs

import requests

from common.boto_utils import BotoUtils
from common.constant import StatusCode
from common.logger import get_logger
from common.utils import send_email_notification
from common.utils import validate_signature
from registry.application.services.organization_publisher_service import OrganizationPublisherService
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.config import SIGNING_SECRET, SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, REGION_NAME
from registry.config import STAGING_URL, ALLOWED_SLACK_USER, SLACK_APPROVAL_CHANNEL_URL, \
    ALLOWED_SLACK_CHANNEL_ID, MAX_SERVICES_SLACK_LISTING, NOTIFICATION_ARN, VERIFICATION_ARN
from registry.constants import UserType, ServiceSupportType, ServiceStatus, OrganizationStatus
from registry.domain.models.service_comment import ServiceComment
from registry.exceptions import InvalidSlackChannelException, InvalidSlackSignatureException, InvalidSlackUserException
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)
boto_util = BotoUtils(region_name=REGION_NAME)


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

    def get_list_of_org_pending_for_approval(self):
        list_of_org_pending_for_approval = OrganizationPublisherService(None, None) \
            .get_approval_pending_organizations(MAX_SERVICES_SLACK_LISTING)
        slack_blocks = self.generate_slack_blocks_for_org_listing_template(list_of_org_pending_for_approval)
        slack_payload = {"blocks": slack_blocks}
        logger.info(f"slack_payload: {slack_payload}")
        response = requests.post(url=SLACK_APPROVAL_CHANNEL_URL, data=json.dumps(slack_payload))
        logger.info(f"{response.status_code} | {response.text}")

    def get_list_of_service_pending_for_approval(self):
        list_of_service_pending_for_approval = \
            ServicePublisherService(username=None, org_uuid=None, service_uuid=None). \
                get_list_of_service_pending_for_approval(limit=MAX_SERVICES_SLACK_LISTING)
        slack_blocks = self.generate_slack_blocks_for_service_listing_template(list_of_service_pending_for_approval)
        slack_payload = {"blocks": slack_blocks}
        logger.info(f"slack_payload: {slack_payload}")
        response = requests.post(url=SLACK_APPROVAL_CHANNEL_URL, data=json.dumps(slack_payload))
        logger.info(f"{response.status_code} | {response.text}")

    def generate_slack_blocks_for_org_listing_template(self, orgs):
        title_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Org Approval Requests*"
            }
        }
        org_listing_slack_blocks = [title_block]
        for org_dict in orgs:
            org_id = "--" if not org_dict["org_id"] else org_dict["org_id"]
            mrkdwn_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Organization Id:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Requested on:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{org_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"requested_at"
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
                            "org_id": org_id,
                            "path": "/org"
                        })
                    }
                ]
            }
            divider_block = {
                "type": "divider"
            }
            org_listing_slack_blocks = org_listing_slack_blocks + [mrkdwn_block, review_button_block, divider_block]
        return org_listing_slack_blocks

    def generate_slack_blocks_for_service_listing_template(self, services):
        title_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Service Approval Requests*"
            }
        }
        service_listing_slack_blocks = [title_block]
        for service_dict in services:
            org_id = "--" if not service_dict["org_id"] else service_dict["org_id"]
            service_id = "--" if not service_dict["service_id"] else service_dict["service_id"]
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
                        "value": json.dumps({
                            "service_id": service_id,
                            "org_id": org_id,
                            "path": "/service"
                        })
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
            org = OrganizationPublisherRepository().get_org_for_org_id(org_id=params["org_id"])
            if org.org_state.state == OrganizationStatus.APPROVAL_PENDING.value:
                self.callback_verification_service(org.uuid, getattr(OrganizationStatus, state).value,
                                                   self._username, comment)
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
                slack_msg = f"Reviews for service with {service.service_id} is successfully submitted."
                # send_slack_notification(slack_msg=slack_msg, slack_url=SLACK_APPROVAL_CHANNEL_URL,
                #                         slack_channel="ai-approvals")
                recipients = [contributor.get("email_id", "") for contributor in service.contributors]
                if not recipients:
                    logger.info(
                        f"Unable to find service contributors for service {service.service_id} under {params['org_id']}")
                    return
                notification_subject = f"Your service {service.service_id} is reviewed"
                notification_message = f"Your service {service.service_id} under {params['org_id']} is reviewed"
                send_email_notification(
                    recipients=recipients, notification_subject=notification_subject,
                    notification_message=notification_message, notification_arn=NOTIFICATION_ARN, boto_util=boto_util)
                logger.info(slack_msg)
            else:
                logger.info("Service state is not valid.")
        else:
            logger.info("Approval type is not valid")

    def callback_verification_service(self, entity_id, state, reviewed_by, comment):
        verification_callback_payload = {
            "verificationStatus": state,
            "comment": comment,
            "reviewed_by": reviewed_by
        }
        verification_callback_event = {
            "queryStringParameters": {
                "entity_id": entity_id
            },
            "body": json.dumps(verification_callback_payload)
        }
        logger.info(f"verification_callback_event: {verification_callback_event}")
        verification_callback_response = boto_util.invoke_lambda(
            VERIFICATION_ARN["DUNS_VERIFICATION"], invocation_type="RequestResponse",
            payload=json.dumps(verification_callback_event))
        logger.info(f"verification_callback_response: {verification_callback_response}")
        if verification_callback_response["statusCode"] != StatusCode.CREATED:
            logger.error(f"callback to verification service for entity_id: {entity_id} state: {state}"
                         f"reviewed_by: {reviewed_by} comment:{comment}")
            raise Exception(f"callback to verification service")

    def create_and_send_view_service_modal(self, org_id, service_id, trigger_id):
        org_uuid, service = ServicePublisherRepository(). \
            get_service_for_given_service_id_and_org_id(org_id=org_id, service_id=service_id)
        service_comment = ServicePublisherRepository(). \
            get_last_service_comment(
            org_uuid=org_uuid, service_uuid=service.uuid, support_type=ServiceSupportType.SERVICE_APPROVAL.value,
            user_type=UserType.SERVICE_PROVIDER.value)
        service_comment == "--" if not service_comment else service_comment
        view = self.generate_view_service_modal(org_id, service, None, service_comment)
        slack_payload = {
            "trigger_id": trigger_id,
            "view": view
        }
        OPEN_SLACK_VIEW_URL = "https://slack.com/api/views.open"
        headers = {"Authorization": SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, "content-type": "application/json"}
        logger.info(f"slack_payload: {slack_payload}")
        response = requests.post(url=OPEN_SLACK_VIEW_URL, data=json.dumps(slack_payload), headers=headers)
        logger.info(f"{response.status_code} | {response.text}")

    def create_and_send_view_org_modal(self, org_id, trigger_id):
        org = OrganizationPublisherRepository().get_org_for_org_id(org_id=org_id)
        view = self.generate_view_org_modal(org, None)
        slack_payload = {
            "trigger_id": trigger_id,
            "view": view
        }
        OPEN_SLACK_VIEW_URL = "https://slack.com/api/views.open"
        headers = {"Authorization": SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, "content-type": "application/json"}
        logger.info(f"slack_payload: {slack_payload}")
        response = requests.post(url=OPEN_SLACK_VIEW_URL, data=json.dumps(slack_payload), headers=headers)
        logger.info(f"{response.status_code} | {response.text}")

    def generate_view_service_modal(self, org_id, service, requested_at, comment):
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
        service_provider_comment_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Comments*\n*{comment}"
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
        blocks = [service_info_display_block, divider_block, service_provider_comment_block, select_approval_state_block, comment_block]
        view["blocks"] = blocks
        return view

    def generate_view_org_modal(self, org, requested_at):
        org_id = ""
        organization_name = ""
        view = {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Org For Approval",
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
        org_info_display_block = {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Organization Id:*\n{org_id}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Organization Name:*\n{organization_name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Approval Platform:*\n{STAGING_URL}/servicedetails/org/{org_id}\n"
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
                    "value": OrganizationStatus.CHANGE_REQUESTED.value,
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
                        "value": OrganizationStatus.APPROVED.value,
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
                        "value": OrganizationStatus.REJECTED.value,
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
                        "value": OrganizationStatus.CHANGE_REQUESTED.value,
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
        blocks = [org_info_display_block, divider_block, select_approval_state_block, comment_block]
        view["blocks"] = blocks
        return view
