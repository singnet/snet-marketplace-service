from common.exception_handler import exception_handler
from common.logger import get_logger
from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.application.schemas.job_schemas import RegistryEventConsumerRequest
from deployer.application.services.job_services import ServiceEventConsumer, JobService

logger = get_logger(__name__)


def registry_event_consumer(event, context):
    events = RegistryEventConsumerRequest.get_events_from_queue(event)

    for e in events:
        request = RegistryEventConsumerRequest.validate_event(e)
        if request.event_name in ["ServiceCreated", "ServiceMetadataModified", "ServiceDeleted"]:
            ServiceEventConsumer().on_event(request)

    return {}


@exception_handler(logger=logger)
def update_transaction_status(event, context):
    JobService().update_transaction_status()
    return {}


@exception_handler(logger=logger)
def check_daemons(event, context):
    JobService().check_daemons()
    return {}


@exception_handler(logger=logger)
def update_daemon_status(event, context):
    request = DaemonRequest.validate_event(event)

    JobService().update_daemon_status(request)

    return {}
