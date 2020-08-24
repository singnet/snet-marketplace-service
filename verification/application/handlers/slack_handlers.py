import json
from urllib.parse import parse_qs

from common.constant import StatusCode
from common.logger import get_logger
from verification.application.services.slack_operation import SlackOperation

logger = get_logger(__name__)


def get_pending_individual_verification(event, context):
    payload_raw = event["body"]
    payload_dict = parse_qs(payload_raw)
    headers = event["headers"]
    logger.info(f"payload:: {payload_dict}")
    logger.info(f"headers:: {headers}")

    slack_chat_operation = SlackOperation(
        username=payload_dict["user_name"][0], channel_id=payload_dict["channel_id"][0])

    slack_chat_operation.validate_slack_request(headers, payload_raw)
    slack_chat_operation.get_pending_individual_verification()
    return {
        'statusCode': StatusCode.OK,
        'body': ""
    }


def slack_interaction_handler(event, context):
    logger.info(f"event:: {event}")
    event_body = event["body"]
    event_body_dict = parse_qs(event_body)
    payload = json.loads(event_body_dict["payload"][0])
    headers = event["headers"]

    slack_chat_operation = SlackOperation(
        username=payload["user"]["username"], channel_id=payload.get("channel", {}).get("id", None))
    slack_chat_operation.validate_slack_request(headers=headers, payload_raw=event_body, ignore=True)
    slack_chat_operation.process_interaction(payload)
    return {
        'statusCode': StatusCode.OK,
        'body': ""
    }

