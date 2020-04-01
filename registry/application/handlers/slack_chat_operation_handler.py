from urllib.parse import parse_qsl

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response
from registry.application.services.slack_chat_operation import SlackChatOperation
from registry.config import SLACK_HOOK, NETWORK_ID
from registry.exceptions import EXCEPTIONS

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_list_of_service_pending_for_approval(event, context):
    payload_raw = event["body"]
    payload_dict = dict(parse_qsl(event["body"]))
    headers = event["headers"]
    logger.info(f"event_body_dict:: {payload_dict}")
    logger.info(f"headers:: {headers}")

    slack_chat_operation = SlackChatOperation(username=payload_dict["user_name"], channel_id=payload_dict["channel_id"])
    slack_chat_operation.validate_slack_request(headers, payload_raw)

    response = slack_chat_operation.get_list_of_service_pending_for_approval()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_list_of_pending_approval_for_slack(event, context):
    payload_raw = event["body"]
    payload_dict = dict(parse_qsl(event["body"]))
    headers = event["headers"]
    logger.info(f"event_body_dict:: {payload_dict}")
    logger.info(f"headers:: {headers}")

    slack_chat_operation = SlackChatOperation(username=payload_dict["user_name"], channel_id=payload_dict["channel_id"])
    slack_chat_operation.validate_slack_request(headers, payload_raw)

    response = slack_chat_operation.get_list_of_organizations_pending_for_approval()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}
    )
