import json

from common.logger import get_logger
from registry.config import NETWORKS, NETWORK_ID
from registry.consumer.organization_event_consumer import OrganizationCreatedAndModifiedEventConsumer
from registry.consumer.service_event_consumer import ServiceCreatedEventConsumer
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)

org_repository = OrganizationPublisherRepository()
service_repository = ServicePublisherRepository()


def get_registry_event_consumer(event):
    if event["name"] in ["OrganizationCreated", "OrganizationModified"]:
        return OrganizationCreatedAndModifiedEventConsumer(
            ws_provider = NETWORKS[NETWORK_ID]["ws_provider"],
            organization_repository = org_repository
        )
    elif event["name"] in ["ServiceCreated", "ServiceMetadataModified"]:
        return ServiceCreatedEventConsumer(
            ws_provider = NETWORKS[NETWORK_ID]["ws_provider"],
            service_repository = service_repository,
            organization_repository = org_repository
        )


def get_payload_from_queue_event(event) -> list[dict]:
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
                    converted_events.append(payload["blockchain_event"])
    return converted_events


def registry_event_consumer_handler(event, context):
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
