from contract_api.consumers.service_event_consumer import (
    ServiceCreatedEventConsumer,
    ServiceMetadataModifiedConsumer,
    ServiceDeletedEventConsumer
)
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.consumers.organization_event_consumer import (
    OrganizationCreatedEventConsumer,
    OrganizationModifiedEventConsumer,
    OrganizationDeletedEventConsumer,
)


def get_organization_event_consumer(event):
    if event["name"] == "OrganizationCreated":
        return OrganizationCreatedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    elif event["name"] == "OrganizationModified":
        return OrganizationModifiedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    elif event["name"] == "OrganizationDeleted":
        return OrganizationDeletedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])


def get_service_event_consumer(event):
    if event["name"] == "ServiceCreated":
        return ServiceCreatedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    elif event["name"] == "ServiceMetadataModified":
        return ServiceMetadataModifiedConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    elif event["name"] == "ServiceDeleted":
        return ServiceDeletedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
