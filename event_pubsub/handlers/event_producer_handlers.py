from event_pubsub.config import NETWORK_ID, NETWORKS, WS_PROVIDER
from event_pubsub.producers.blockchain_event_producer import RegistryEventProducer, MPEEventProducer, RFAIEventProducer
from event_pubsub.repository import Repository

registry_event_producer = RegistryEventProducer(WS_PROVIDER, Repository(NETWORKS))
mpe_event_producer = MPEEventProducer(WS_PROVIDER, Repository(NETWORKS))
rfai_event_producer=RFAIEventProducer(WS_PROVIDER, Repository(NETWORKS))


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


def rfai_event_producer_handler(event,context):
    try:
        rfai_event_producer.produce_event(NETWORK_ID)
    except Exception as e:
        raise e
