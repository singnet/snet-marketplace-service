from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import handle_exception_with_slack_notification
from event_pubsub.config import NETWORKS, NETWORK_ID, SLACK_HOOK, HTTP_PROVIDER
from event_pubsub.producers.blockchain_event_producer import MPEEventProducer, RFAIEventProducer, RegistryEventProducer, \
    TokenStakeEventProducer
from event_pubsub.repository import Repository

registry_event_producer = RegistryEventProducer(HTTP_PROVIDER, Repository(NETWORKS))
mpe_event_producer = MPEEventProducer(HTTP_PROVIDER, Repository(NETWORKS))
rfai_event_producer = RFAIEventProducer(HTTP_PROVIDER, Repository(NETWORKS))
token_stake_event_producer = TokenStakeEventProducer(HTTP_PROVIDER, Repository(NETWORKS))

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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def token_stake_event_producer_handler(event, context):
    try:
        token_stake_event_producer.produce_event(NETWORK_ID)
    except Exception as e:
        raise e
