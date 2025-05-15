import json

from common.logger import get_logger
from common.utils import Utils, generate_lambda_response
from common.utils import handle_exception_with_slack_notification
from contract_api.config import NETWORK_ID, SLACK_HOOK
from contract_api.application.service.registry_service import RegistryService


util = Utils()
logger = get_logger(__name__)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def save_offchain_attribute(event, context):
    logger.info(f"Got save offchain attribute event:: {event}")
    org_id = event["pathParameters"]["orgId"]
    service_id = event["pathParameters"]["serviceId"]
    attributes = json.loads(event["body"])
    response = RegistryService(org_id=org_id, service_id=service_id).save_offchain_service_attribute(
        new_offchain_attributes=attributes)
    logger.info(f"Response data: {response}")
    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled=True)
