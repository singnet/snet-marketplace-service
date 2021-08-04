from common.constant import StatusCode
from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, generate_lambda_response
from event_pubsub.config import SLACK_HOOK, NETWORK_ID
from event_pubsub.services.raw_events_service import RawEventsService

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_raw_event_details(event, context):
    logger.info(f"get_raw_event_details :: event :: {event}")
    transaction_hash_list = event["transaction_hash_list"]
    event_name = event["event_name"]
    response = RawEventsService().get_raw_events(
        transaction_hash_list=transaction_hash_list,
        event_name=event_name
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )