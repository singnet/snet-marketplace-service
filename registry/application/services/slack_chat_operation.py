import json
from datetime import datetime

import requests

from common import boto_utils
from common.constant import StatusCode
from common.logger import get_logger
from common.utils import send_email_notification, datetime_to_string
from common.utils import validate_signature
from registry.application.services.organization_publisher_service import OrganizationPublisherService
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.config import SIGNING_SECRET, SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, REGION_NAME
from registry.config import STAGING_URL, ALLOWED_SLACK_USER, SLACK_APPROVAL_CHANNEL_URL, \
    ALLOWED_SLACK_CHANNEL_ID, MAX_SERVICES_SLACK_LISTING, NOTIFICATION_ARN, VERIFICATION_ARN
from registry.constants import OrganizationAddressType, OrganizationType
from registry.constants import UserType, ServiceSupportType, ServiceStatus, OrganizationStatus
from registry.domain.models.comment import Comment
from registry.domain.models.service_comment import ServiceComment
from registry.exceptions import InvalidSlackChannelException, InvalidSlackSignatureException, InvalidSlackUserException, \
    InvalidOrganizationType
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)
boto_util = boto_utils.BotoUtils(region_name=REGION_NAME)


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
        response = requests.post(url=SLACK_APPROVAL_CHANNEL_URL, data=json.dumps(slack_payload))
        logger.info(f"{response.status_code} | {response.text}")

    def get_list_of_service_pending_for_approval(self):
        list_of_service_pending_for_approval = \
            ServicePublisherService(username=None, org_uuid=None, service_uuid=None). \
                get_list_of_service_pending_for_approval(limit=MAX_SERVICES_SLACK_LISTING)
        slack_blocks = self.generate_slack_blocks_for_service_listing_template(list_of_service_pending_for_approval)
        slack_payload = {"blocks": slack_blocks}
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
            org_id = "None" if not org_dict["org_id"] else org_dict["org_id"]
            org_name = "None" if not org_dict.get("org_name", "None") else org_dict.get("org_name", "None")
            mrkdwn_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Organization Id:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Organization Name:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{org_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{org_name}"
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
            org_id = "None" if not service_dict["org_id"] else service_dict["org_id"]
            service_id = "None" if not service_dict["service_id"] else service_dict["service_id"]
            service_name = "None" if not service_dict.get("display_name", "None") else service_dict.get("display_name",
                                                                                                        "None")
            mrkdwn_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Service Id:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Service Name:*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"<{STAGING_URL}/servicedetails/org/{org_id}/service/{service_id}|{service_id}>"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{service_name}"
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
            if org.org_state.state in [OrganizationStatus.APPROVAL_PENDING.value, OrganizationStatus.ONBOARDING.value]:
                if org.org_type == OrganizationType.ORGANIZATION.value:
                    self.callback_verification_service(org.uuid, getattr(OrganizationStatus, state).value,
                                                       self._username, comment)
                elif org.org_type == OrganizationType.INDIVIDUAL.value:
                    OrganizationPublisherRepository().update_organization_status(
                        org.uuid, getattr(OrganizationStatus, state).value, self._username,
                        Comment(comment, self._username, datetime_to_string(datetime.now())))

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
        verification_callback_response = boto_util.invoke_lambda(
            VERIFICATION_ARN["DUNS_CALLBACK"], invocation_type="Event",
            payload=json.dumps(verification_callback_event))
        if verification_callback_response["StatusCode"] != StatusCode.ACCEPTED:
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
        comment = "No comment" if not service_comment else service_comment.comment
        view = self.generate_view_service_modal(org_id, service, None, comment)
        slack_payload = {
            "trigger_id": trigger_id,
            "view": view
        }
        OPEN_SLACK_VIEW_URL = "https://slack.com/api/views.open"
        headers = {"Authorization": SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, "content-type": "application/json"}
        response = requests.post(url=OPEN_SLACK_VIEW_URL, data=json.dumps(slack_payload), headers=headers)
        logger.info(f"{response.status_code} | {response.text}")

    def create_and_send_view_org_modal(self, org_id, trigger_id):
        org = OrganizationPublisherRepository().get_org_for_org_id(org_id=org_id)
        if not org:
            logger.info("org not found")
        comment = "No comment"
        if org.org_type == OrganizationType.ORGANIZATION.value:
            comment = self.get_verification_latest_comments(org.uuid)
        elif org.org_type == OrganizationType.INDIVIDUAL.value:
            comment = org.org_state.get_latest_comment()
        comment = "No comment" if not comment else comment
        view = self.generate_view_org_modal(org, None, comment)
        slack_payload = {
            "trigger_id": trigger_id,
            "view": view
        }
        OPEN_SLACK_VIEW_URL = "https://slack.com/api/views.open"
        headers = {"Authorization": SLACK_APPROVAL_OAUTH_ACCESS_TOKEN, "content-type": "application/json"}
        response = requests.post(url=OPEN_SLACK_VIEW_URL, data=json.dumps(slack_payload), headers=headers)
        logger.info(f"{response.status_code} | {response.text}")

    def get_verification_latest_comments(self, org_uuid):
        verification_status_event = {
            "queryStringParameters": {
                "type": "DUNS",
                "entity_id": org_uuid
            },
            "body": None,
            "pathParameters": None
        }

        verification_status_response = boto_util.invoke_lambda(lambda_function_arn=VERIFICATION_ARN["GET_VERIFICATION"],
                                                               invocation_type="RequestResponse",
                                                               payload=json.dumps(verification_status_event))

        if verification_status_response["statusCode"] != 200:
            raise Exception(f"Failed to get verification status for org_uuid: {org_uuid}")
        verification_status = json.loads(verification_status_response["body"])["data"]
        if "duns" not in verification_status or "comments" not in verification_status["duns"]:
            logger.error(str(verification_status))
            raise Exception(f"Failed to parse verification status for org_uuid: {org_uuid}")

        comments = verification_status["duns"]["comments"]
        if len(comments) == 0:
            return ""
        latest_comment = comments[0]
        for comment in comments:
            if comment["created_at"] > latest_comment["created_at"]:
                latest_comment = comment
        return latest_comment["comment"]

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
                        "text": "Request changes."
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
                            "text": "Allow user to publish service."
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
                            "text": "Reject user request."
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
        blocks = [service_info_display_block, divider_block, service_provider_comment_block,
                  select_approval_state_block, comment_block]
        view["blocks"] = blocks
        return view

    def generate_view_org_modal(self, org, requested_at, comment):
        org_id = "None" if not org.id else org.id
        organization_name = "None" if not org.name else org.name
        duns_no = "None" if not org.duns_no else org.duns_no
        phone_no = "None"
        for contact in org.contacts:
            if contact.get("contact_type") == "general":
                phone_no = contact.get("phone", None)
        url = "None" if not org.url else org.url
        headquater_address = {}
        mailing_address = {}
        for address in org.addresses:
            if address.address_type == OrganizationAddressType.HEAD_QUARTER_ADDRESS.value:
                headquater_address = address.to_response()
            if address.address_type == OrganizationAddressType.MAIL_ADDRESS.value:
                mailing_address = address.to_response()

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
        if org.org_type == OrganizationType.ORGANIZATION.value:
            org_top_info_display_block = {
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
                        "text": f"*Duns Number:*\n{duns_no}\n"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Website URL:*\n{url}\n"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Phone Number:*\n{phone_no}\n"
                    }
                ]
            }
        elif org.org_type == OrganizationType.INDIVIDUAL.value:
            org_top_info_display_block = {
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
                        "text": f"*Registration ID:*\n{'None' if not org.registration_id else org.registration_id}\n"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Registration Type:*\n{'None' if not org.registration_type else org.registration_type}\n"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Website URL:*\n{url}\n"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Phone Number:*\n{phone_no}\n"
                    }
                ]
            }
        else:
            raise InvalidOrganizationType()

        org_address_title_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Addresses*"
            }
        }
        org_headquater_address_block = {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Headquarter Address:*\n\tApartment: {headquater_address.get('apartment', '')}\n\t"
                            f"Street Address: {headquater_address.get('street_address', '')}\n\t"
                            f"City: {headquater_address.get('city', '')}\n\t"
                            f"State: {headquater_address.get('state', '')}\n\t"
                            f"Pincode: {headquater_address.get('pincode', '')}\n\t"
                            f"Country: {headquater_address.get('country', '')}\n"
                }
            ]
        }
        org_mailing_address_block = {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Mailing Address:*\n\tApartment: {mailing_address.get('apartment', '')}\n\t"
                            f"Street Address: {mailing_address.get('street_address', '')}\n\t"
                            f"City: {mailing_address.get('city', '')}\n\t"
                            f"State: {mailing_address.get('state', '')}\n\t"
                            f"Pincode: {mailing_address.get('pincode', '')}\n\t"
                            f"Country: {mailing_address.get('country', '')}\n"
                }
            ]
        }
        org_info_display_blocks = [org_top_info_display_block, org_address_title_block, org_headquater_address_block,
                                   org_mailing_address_block]
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
                        "text": "Request changes."
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
                            "text": "Allow user to publish organization."
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
                            "text": "Rejects user request."
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
        org_comment_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Comments*\n*{comment}"
            }
        }
        blocks = org_info_display_blocks + [divider_block, org_comment_block, select_approval_state_block,
                                            comment_block]
        view["blocks"] = blocks
        return view
