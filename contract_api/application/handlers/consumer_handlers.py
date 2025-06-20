from common.constant import StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response
from common.exception_handler import exception_handler
from contract_api.application.schemas.consumer_schemas import MpeEventConsumerRequest, RegistryEventConsumerRequest
from contract_api.application.consumers.consumer_factory import (
    get_registry_event_consumer
)
from contract_api.application.consumers.mpe_event_consumer import MPEEventConsumer
from contract_api.application.consumers.service_event_consumer import ServiceCreatedDeploymentEventHandler


logger = get_logger(__name__)


def mpe_event_consumer(event, context):
    events = MpeEventConsumerRequest.get_events_from_queue(event)

    for e in events:
        request = MpeEventConsumerRequest.validate_event(e)
        MPEEventConsumer().on_event(request)

    return {}


def registry_event_consumer(event, context):
    events = RegistryEventConsumerRequest.get_events_from_queue(event)

    for e in events:
        request = RegistryEventConsumerRequest.validate_event(e)
        consumer = get_registry_event_consumer(request)
        if consumer is None:
            logger.info(f"Unhandled Registry event: {e}")
            continue
        consumer.on_event(request)

    return {}


@exception_handler(logger=logger)
def manage_service_deployment(event, context):
    request = RegistryEventConsumerRequest.validate_event(event)

    ServiceCreatedDeploymentEventHandler().on_event(request)

    return generate_lambda_response(200, StatusCode.OK)
