import json

from aws_xray_sdk.core import patch_all
from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import Utils, generate_lambda_response
from common.utils import handle_exception_with_slack_notification
from contract_api.config import NETWORK_ID, SLACK_HOOK
from contract_api.application.service.registry_service import RegistryService

# patch_all()

util = Utils()
logger = get_logger(__name__)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def save_offchain_attribute(event, context):
    logger.info(f"Got save offchain attribute event:: {event}")
    org_id = event["pathParameters"]["orgId"]
    service_id = event["pathParameters"]["serviceId"]
    payload = json.loads(event["body"])
    response = RegistryService(org_id=org_id, service_id=service_id).save_offchain_service_attribute(
        new_offchain_attributes=payload)
    return generate_lambda_response(
        200, {"status": "success", "data": response}, cors_enabled=True)
