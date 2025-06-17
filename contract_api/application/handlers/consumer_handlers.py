from common.constant import StatusCode
from common.logger import get_logger
from common.utils import Utils, generate_lambda_response
from common.exception_handler import exception_handler
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.consumers.consumer_factory import (
    get_payload_from_queue_event,
    get_registry_event_consumer
)
from contract_api.consumers.mpe_event_consumer import MPEEventConsumer
from contract_api.consumers.service_event_consumer import ServiceCreatedDeploymentEventHandler

logger = get_logger(__name__)
util=Utils()


def mpe_event_consumer(event, context):
    logger.info(f"Got MPE event from queue {event}")
    events = get_payload_from_queue_event(event)
    consumer = MPEEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    for e in events:
        logger.info(f"Processing MPE event: {e}")
        consumer.on_event(e)
    return {}


def registry_event_consumer(event, context):
    logger.info(f"Got Registry event {event}")
    events = get_payload_from_queue_event(event)

    for e in events:
        consumer = get_registry_event_consumer(e)
        if consumer is None:
            logger.info(f"Unhandled Registry event: {e}")
            continue
        logger.info(f"Processing Registry event: {e}")
        consumer.on_event(e)
    return {}


@exception_handler(logger=logger)
def manage_service_deployment(event, context):
    service_deployment_handler = ServiceCreatedDeploymentEventHandler(NETWORKS[NETWORK_ID]["ws_provider"])
    service_deployment_handler.on_event(event)
    return generate_lambda_response(200, StatusCode.OK)
