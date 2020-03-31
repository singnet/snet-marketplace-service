from registry.application.services.slack_chat_operation import SlackChatOperation
from registry.exceptions import BadRequestException, EXCEPTIONS
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

    slack_chat_operation = SlackChatOperation(
        username=event_body_dict["user_name"][0], channel_id=event_body_dict["channel_id"][0])

    # validate slack channel
    if not slack_chat_operation.validate_slack_channel_id():
        raise BadRequestException()

    # validate slack user
    if not slack_chat_operation.validate_slack_user():
        raise BadRequestException()

    # validate slack signature
    slack_signature_message = slack_chat_operation.generate_slack_signature_message(
        request_timestamp=headers["X-Slack-Request-Timestamp"], event_body=event_body)
    if not slack_chat_operation.validate_slack_signature(
            signature=headers["X-Slack-Signature"], message=slack_signature_message):
        raise BadRequestException()

    # get services for given org_id
    return slack_chat_operation.get_list_of_service_pending_for_approval()
