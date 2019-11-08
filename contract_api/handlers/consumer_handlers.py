from common.constant import StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response
from contract_api.config import NETWORKS
from contract_api.config import NETWORK_ID
from contract_api.consumers.consumer_factory import get_organization_event_consumer, get_service_event_consumer
from contract_api.consumers.mpe_event_consumer import MPEEventConsumer

logger = get_logger(__name__)


def organization_event_consumer_handler(event, context):
    try:

        organization_event_consumer = get_organization_event_consumer(event)
        organization_event_consumer.on_event(event)

        return generate_lambda_response(200, StatusCode.OK)
    except Exception as e:
        logger.exception(f"error  {str(e)} while processing event {event}")

        return generate_lambda_response(500, str(e))


def service_event_consumer_handler(event, context):
    try:
        service_event_consumer = get_service_event_consumer(event)
        service_event_consumer.on_event(event)
        return generate_lambda_response(200, StatusCode.OK)
    except Exception as e:
        logger.exception(f"error  {str(e)} while processing event {event}")
        return generate_lambda_response(500, str(e))


def mpe_event_consumer_handler(event, context):
    try:
        MPEEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"]).on_event(event)
        return generate_lambda_response(200, StatusCode.OK)

    except Exception as e:
        logger.exception(f"error  {str(e)} while processing event {event}")
        return generate_lambda_response(500, str(e))
