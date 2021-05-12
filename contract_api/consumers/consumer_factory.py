from contract_api.consumers.service_event_consumer import ServiceCreatedEventConsumer, ServiceMetadataModifiedConsumer, \
     SeviceDeletedEventConsumer
from contract_api.config import NETWORKS, NETWORK_ID, IPFS_URL
from contract_api.consumers.organization_event_consumer import OrganizationCreatedEventConsumer, OrganizationModifiedEventConsumer, \
    OrganizationDeletedEventConsumer


def get_organization_event_consumer(event):
    if event['name'] == "OrganizationCreated":
        return OrganizationCreatedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'],
                                                IPFS_URL['port'])
    elif event['name'] == 'OrganizationModified':
        return OrganizationModifiedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'],
                                                 IPFS_URL['port'])
    elif event['name'] == "OrganizationDeleted":
        return OrganizationDeletedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'],
                                                IPFS_URL['port'])


def get_service_event_consumer(event):
    if event['name'] == 'ServiceCreated':
        return ServiceCreatedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'], IPFS_URL['port'])

    elif event['name'] == 'ServiceMetadataModified':
        return ServiceMetadataModifiedConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'], IPFS_URL['port'])

    elif event['name'] == 'ServiceDeleted':
        return SeviceDeletedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'], IPFS_URL['port'])
