from common.constant import StatusCode
from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification, generate_lambda_response
from event_pubsub.config import SLACK_HOOK, NETWORK_ID
from event_pubsub.services.event_pubsub_service import EventPubsubService

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_mpe_processed_transactions(event, context):
    logger.info(f"get_processed_transactions :: event :: {event}")
    transaction_list = event["transaction_list"]
    response = EventPubsubService().get_mpe_processed_transactions(
        transaction_list=transaction_list
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )