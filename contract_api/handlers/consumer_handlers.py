from common.constant import StatusCode
from common.utils import generate_lambda_response
from consumers.mpe_event_consumer import MPEEventConsumer
from consumers.organization_event_consumer import OrganizationEventConsumer
from consumers.service_event_consumer import ServiceEventConsumer


def organization_event_consumer_handler(event, context):
    try:

        OrganizationEventConsumer().on_event(event)
        return generate_lambda_response(200,StatusCode.OK)
    except Exception as e:
        print(e)
        return generate_lambda_response(500,str(e))


def service_event_consumer_handler(event, context):
    try:
        ServiceEventConsumer().on_event(event)
        return generate_lambda_response(200, StatusCode.OK)
    except Exception as e:
        print(e)
        return generate_lambda_response(500, str(e))


def mpe_event_consumer_handler(event,context):
    try:
        MPEEventConsumer().on_event(event)
        return generate_lambda_response(200, StatusCode.OK)

    except Exception as e:
        print(e)
        return generate_lambda_response(500, str(e))
