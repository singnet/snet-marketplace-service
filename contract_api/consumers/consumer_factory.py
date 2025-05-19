import json

from contract_api.config import NETWORKS, NETWORK_ID
from common.logger import get_logger
from contract_api.consumers.service_event_consumer import (
    ServiceCreatedEventConsumer,
    ServiceDeletedEventConsumer
)
from contract_api.consumers.organization_event_consumer import (
    OrganizationCreatedEventConsumer,
    OrganizationDeletedEventConsumer,
)


logger = get_logger(__name__)


def get_payload_from_queue_event(event):
    converted_events = []
    records = event.get("Records", [])
    logger.info(f"Event records: {records}")
    if records:
        for record in records:
            body = record.get("body")
            if body:
                parsed_body = json.loads(body)
                message = parsed_body.get("Message")
                if message:
                    payload = json.loads(message)
                    converted_events.append(payload)
    return converted_events


def get_registry_event_consumer(event):
    if event["name"] == "ServiceCreated" or event["name"] == "ServiceMetadataModified":
        return ServiceCreatedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    elif event["name"] == "ServiceDeleted":
        return ServiceDeletedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    elif event["name"] == "OrganizationCreated" or event["name"] == "OrganizationModified":
        return OrganizationCreatedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    elif event["name"] == "OrganizationDeleted":
        return OrganizationDeletedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"])
    return None
