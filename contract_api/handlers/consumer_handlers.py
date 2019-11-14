from common.constant import StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response, Utils
from contract_api.config import NETWORKS, SLACK_HOOK
from contract_api.config import NETWORK_ID
from contract_api.consumers.consumer_factory import get_organization_event_consumer, get_service_event_consumer
from contract_api.consumers.mpe_event_consumer import MPEEventConsumer

logger = get_logger(__name__)
util=Utils()


def organization_event_consumer_handler(event, context):
    try:
        logger.info(f"Got Organization Event {event}")
        organization_event_consumer = get_organization_event_consumer(event)
        organization_event_consumer.on_event(event)

        return generate_lambda_response(200, StatusCode.OK)
    except Exception as e:
        logger.exception(f"error  {str(e)} while processing event {event}")
        util.report_slack("ERROR",f"got error : {str(e)} \n for event : {event}",SLACK_HOOK)

        return generate_lambda_response(500, str(e))


def service_event_consumer_handler(event, context):
    logger.info(f"Got Service Event {event}")
    try:
        service_event_consumer = get_service_event_consumer(event)
        service_event_consumer.on_event(event)
        return generate_lambda_response(200, StatusCode.OK)
    except Exception as e:
        logger.exception(f"error  {str(e)} while processing event {event}")
        util.report_slack("ERROR", f"got error :  {str(e)} \n for event : {event}", SLACK_HOOK)
        return generate_lambda_response(500, str(e))


def mpe_event_consumer_handler(event, context):
    logger.info(f"Got MPE Event {event}")
    try:
        MPEEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"]).on_event(event)
        return generate_lambda_response(200, StatusCode.OK)

    except Exception as e:
        logger.exception(f"error  {str(e)} while processing event {event}")
        util.report_slack("ERROR", f"got error :  {str(e)} \n for event : {event}", SLACK_HOOK)
        return generate_lambda_response(500, str(e))
