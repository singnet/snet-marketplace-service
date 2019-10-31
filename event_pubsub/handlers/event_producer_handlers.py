from event_pubsub.config import NETWORK_ID, NETWORKS, WS_PROVIDER
from event_pubsub.producers.blockchain_event_producer import RegistryEventProducer, MPEEventProducer
from event_pubsub.repository import Repository


def registry_event_producer_handler(event, context):
    try:
        blockchain_event_producer = RegistryEventProducer(WS_PROVIDER, Repository(NETWORKS))
        blockchain_event_producer.produce_event(NETWORK_ID)
    except Exception as e:
        raise e


def mpe_event_producer_handler(event, context):
    try:
        blockchain_event_producer = MPEEventProducer(WS_PROVIDER, Repository(NETWORKS))
        blockchain_event_producer.produce_event(NETWORK_ID)
    except Exception as e:
        raise e
