import json
from registry.application.services.slack_chat_operation import SlackChatOperation
from registry.exceptions import BadRequestException, EXCEPTIONS
from registry.config import SLACK_HOOK, NETWORK_ID
from urllib.parse import parse_qs
from common.exception_handler import exception_handler
from common.logger import get_logger

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_list_of_org_pending_for_approval(event, context):
    payload_raw = event["body"]
    payload_dict = parse_qs(payload_raw)
    headers = event["headers"]
    logger.info(f"payload:: {payload_dict}")
    logger.info(f"headers:: {headers}")

    slack_chat_operation = SlackChatOperation(
        username=payload_dict["user_name"][0], channel_id=payload_dict["channel_id"][0])
    # validate slack request
    slack_chat_operation.validate_slack_request(headers, payload_raw)
    # get services for given org_id
    slack_chat_operation.get_list_of_org_pending_for_approval()
    return {
        'statusCode': 200,
        'body': ""
    }


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_list_of_service_pending_for_approval(event, context):
    payload_raw = event["body"]
    payload_dict = parse_qs(payload_raw)
    headers = event["headers"]
    logger.info(f"payload:: {payload_dict}")
    logger.info(f"headers:: {headers}")

    slack_chat_operation = SlackChatOperation(
        username=payload_dict["user_name"][0], channel_id=payload_dict["channel_id"][0])
    # validate slack request
    slack_chat_operation.validate_slack_request(headers, payload_raw)
    # get services for given org_id
    slack_chat_operation.get_list_of_service_pending_for_approval()
    return {
        'statusCode': 200,
        'body': ""
    }


def slack_interaction_handler(event, context):
    logger.info(f"event:: {event}")
    event_body = event["body"]
    event_body_dict = parse_qs(event_body)
    payload = json.loads(event_body_dict["payload"][0])
    headers = event["headers"]

    slack_chat_operation = SlackChatOperation(
        username=payload["user"]["username"], channel_id=payload.get("channel", {}).get("id", None))
    # validate slack request
    slack_chat_operation.validate_slack_request(headers=headers, payload_raw=event_body, ignore=True)

    data = {}
    if payload["type"] == "block_actions":
        for action in payload["actions"]:
            if "button" == action.get("type"):
                data = json.loads(action.get("value", {}))
        if not data:
            raise BadRequestException()
        if data["path"] == "/service":
            org_id = data["org_id"]
            service_id = data["service_id"]
            slack_chat_operation.\
                create_and_send_view_service_modal(org_id=org_id, service_id=service_id, trigger_id=payload["trigger_id"])
        elif data["path"] == "/org":
            org_id = data["org_id"]
            slack_chat_operation.create_and_send_view_org_modal(org_id=org_id, trigger_id=payload["trigger_id"])
        else:
            raise BadRequestException()
    elif payload["type"] == "view_submission":
        approval_type = "service" if payload["view"]["title"]["text"] == "Service For Approval" else ""
        approval_type = "organization" if payload["view"]["title"]["text"] == "Org For Approval" else approval_type
        review_request_state = \
            payload["view"]["state"]["values"]["approval_state"]["selection"]["selected_option"]["value"]
        comment = payload["view"]["state"]["values"]["review_comment"]["comment"]["value"]
        params = {}
        if approval_type == "service":
            params = {
                "org_id": payload["view"]["blocks"][0]["fields"][0]["text"].split("\n")[1],
                "service_id": payload["view"]["blocks"][0]["fields"][1]["text"].split("\n")[1]
            }
        elif approval_type == "organization":
            params = {"org_id": payload["view"]["blocks"][0]["fields"][0]["text"].split("\n")[1]}
        response = slack_chat_operation.process_approval_comment(approval_type=approval_type,
                                                                 state=review_request_state,
                                                                 comment=comment, params=params)
    return {
        'statusCode': 200,
        'body': ""
    }