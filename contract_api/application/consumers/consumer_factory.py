from contract_api.application.schemas.consumer_schemas import RegistryEventConsumerRequest
from common.logger import get_logger
from contract_api.application.consumers.service_event_consumers import (
    ServiceCreatedEventConsumer,
    ServiceDeletedEventConsumer
)
from contract_api.application.consumers.organization_event_consumers import (
    OrganizationCreatedEventConsumer,
    OrganizationDeletedEventConsumer,
)


logger = get_logger(__name__)


def get_registry_event_consumer(request: RegistryEventConsumerRequest):
    if request.event_name == "ServiceCreated" or request.event_name == "ServiceMetadataModified":
        return ServiceCreatedEventConsumer()
    elif request.event_name == "ServiceDeleted":
        return ServiceDeletedEventConsumer()
    elif request.event_name == "OrganizationCreated" or request.event_name == "OrganizationModified":
        return OrganizationCreatedEventConsumer()
    elif request.event_name == "OrganizationDeleted":
        return OrganizationDeletedEventConsumer()
    return None
