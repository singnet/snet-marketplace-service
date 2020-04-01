import json
from registry.application.services.slack_chat_operation import SlackChatOperation
from registry.exceptions import BadRequestException, EXCEPTIONS, InvalidSlackChannelException, \
    InvalidSlackSignatureException, InvalidSlackUserException
from registry.config import SLACK_HOOK, NETWORK_ID
from urllib.parse import parse_qs
from common.exception_handler import exception_handler
from common.logger import get_logger

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_list_of_service_pending_for_approval(event, context):
    event_body = event["body"]
    event_body_dict = parse_qs(event_body)
    headers = event["headers"]
    logger.info(f"event_body_dict:: {event_body_dict}")
    logger.info(f"headers:: {headers}")

    slack_chat_operation = SlackChatOperation(
        username=event_body_dict["user_name"][0], channel_id=event_body_dict["channel_id"][0])

    # validate slack channel
    if not slack_chat_operation.validate_slack_channel_id():
        raise InvalidSlackChannelException()

    # validate slack user
    if not slack_chat_operation.validate_slack_user():
        raise InvalidSlackUserException()

    # validate slack signature
    slack_signature_message = slack_chat_operation.generate_slack_signature_message(
        request_timestamp=headers["X-Slack-Request-Timestamp"], event_body=event_body)
    if not slack_chat_operation.validate_slack_signature(
            signature=headers["X-Slack-Signature"], message=slack_signature_message):
        raise InvalidSlackSignatureException()

    # get services for given org_id
    slack_chat_operation.get_list_of_service_pending_for_approval()
    return {
        'statusCode': 200,
        'body': ""
    }


def slack_interaction_handler(event, context):
    event_body = event["body"]
    event_body_dict = parse_qs(event_body)
    payload= json.loads(event_body_dict["payload"][0])
    headers = event["headers"]
    logger.info(f"event_body_dict:: {event_body_dict}")
    logger.info(f"headers:: {headers}")

    slack_chat_operation = SlackChatOperation(
        username=payload["user"]["username"], channel_id=payload.get("channel", {}).get("id", None))

    # validate slack channel
    if not slack_chat_operation.validate_slack_channel_id():
        if not payload["type"] == "view_submission":
            InvalidSlackChannelException()

    # validate slack user
    if not slack_chat_operation.validate_slack_user():
        raise InvalidSlackUserException()

    # validate slack signature
    slack_signature_message = slack_chat_operation.generate_slack_signature_message(
        request_timestamp=headers["X-Slack-Request-Timestamp"], event_body=event_body)
    if not slack_chat_operation.validate_slack_signature(
            signature=headers["X-Slack-Signature"], message=slack_signature_message):
        raise InvalidSlackSignatureException()

    data = {}
    if payload["type"] == "block_actions":
        for action in payload["actions"]:
            if "button" == action.get("type"):
                data = json.loads(action.get("value", {}))
        if not data:
            raise BadRequestException()
        if data["path"] == "/service":
            service_uuid = data["service_uuid"]
            # slack_chat_operation.send_service_modal()
        elif data["path"] == "/org":
            org_uuid = data["org_uuid"]
            # slack_chat_operation.send_org_modal()
        else:
            raise BadRequestException()
    elif payload["type"] == "view_submission":
        pass

