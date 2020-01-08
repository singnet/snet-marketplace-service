from common.constant import StatusCode
from common.logger import get_logger
from common.utils import generate_lambda_response, handle_exception_with_slack_notification
from registry.config import IPFS_URL, NETWORKS, NETWORK_ID, SLACK_HOOK
from registry.consumer.organization_event_consumer import OrganizationCreatedEventConsumer, \
    OrganizationModifiedEventConsumer

logger = get_logger(__name__)


def get_organization_event_consumer(event):
    if event['name'] == "OrganizationCreated":
        return OrganizationCreatedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'],
                                                IPFS_URL['port'])
    elif event['name'] == 'OrganizationModified':
        return OrganizationModifiedEventConsumer(NETWORKS[NETWORK_ID]["ws_provider"], IPFS_URL['url'],
                                                 IPFS_URL['port'])


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def organization_event_consumer_handler(event, context):
    logger.info(f"Got Organization Event {event}")
    organization_event_consumer = get_organization_event_consumer(event)
    organization_event_consumer.on_event(event)

    return generate_lambda_response(200, StatusCode.OK)
