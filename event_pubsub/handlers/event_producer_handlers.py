from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification
from event_pubsub.config import NETWORKS, NETWORK_ID, SLACK_HOOK, WS_PROVIDER
from event_pubsub.producers.blockchain_event_producer import MPEEventProducer, RFAIEventProducer, RegistryEventProducer
from event_pubsub.repository import Repository

registry_event_producer = RegistryEventProducer(WS_PROVIDER, Repository(NETWORKS))
mpe_event_producer = MPEEventProducer(WS_PROVIDER, Repository(NETWORKS))
rfai_event_producer = RFAIEventProducer(WS_PROVIDER, Repository(NETWORKS))

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def registry_event_producer_handler(event, context):
    try:

        registry_event_producer.produce_event(NETWORK_ID)
    except Exception as e:
        raise e


def mpe_event_producer_handler(event, context):
    try:

        mpe_event_producer.produce_event(NETWORK_ID)
    except Exception as e:
        raise e


def rfai_event_producer_handler(event, context):
    try:
        rfai_event_producer.produce_event(NETWORK_ID)
    except Exception as e:
        raise e
