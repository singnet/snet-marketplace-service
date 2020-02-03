import json

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from registry.application.services.organization_publisher_service import OrganizationPublisherService
from registry.config import SLACK_HOOK, NETWORK_ID
from registry.constants import AddOrganizationActions
from registry.exceptions import EXCEPTIONS, BadRequestException

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_all_org(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    response = OrganizationPublisherService(None, username).get_all_org_for_user()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def add_org(event, context):
    payload = json.loads(event["body"])
    required_keys = []
    action = event["queryStringParameters"].get("action", None)
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    org_uuid = payload.get("org_uuid", None)
    org_service = OrganizationPublisherService(org_uuid, username)
    if action == AddOrganizationActions.DRAFT.value:
        response = org_service.add_organization_draft(payload)
    elif action == AddOrganizationActions.SUBMIT.value:
        response = org_service.submit_org_for_approval(payload)
    else:
        raise Exception("Invalid action")
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def publish_org_on_ipfs(event, context):
    path_parameters = event["pathParameters"]
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if "org_id" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    response = OrganizationPublisherService(org_uuid, username).publish_org_to_ipfs()

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def save_transaction_hash(event, context):
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if "org_id" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    response = OrganizationPublisherService(org_uuid, username).save_transaction_hash_for_publish_org(
        payload['transaction_hash'],
        payload['wallet_address'])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
