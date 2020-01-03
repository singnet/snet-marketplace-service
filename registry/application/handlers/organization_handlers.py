import json

from common.constant import StatusCode
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import validate_dict, handle_exception_with_slack_notification, generate_lambda_response, \
    validate_dict_list
from registry.config import SLACK_HOOK, NETWORK_ID
from registry.domain.services.organization_service import OrganizationService
from registry.constants import PostOrganizationActions

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def add_org(event, context):
    payload = json.loads(event["body"])
    action = event["queryStringParameters"]["action"]
    required_keys = ["org_id", "org_uuid", "org_name", "org_type", "metadata_ipfs_hash", "description",
                     "short_description", "url", "contacts", "assets"]

    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    org_service = OrganizationService()
    if action == PostOrganizationActions.DRAFT.value:
        response = org_service.add_organization_draft(payload, username)
    elif action == PostOrganizationActions.SUBMIT.value:
        response = org_service.add_organization_draft(payload, username)
        org_service.submit_org_for_approval(response["org_uuid"], username)
    else:
        raise Exception("Invalid action")

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def publish_org(event, context):
    path_parameters = event["pathParameters"]
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if "org_id" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    response = OrganizationService().publish_org_to_ipfs(org_uuid, username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def save_transaction_hash_for_publish_org(event, context):
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if "org_id" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    response = OrganizationService().save_transaction_hash_for_publish_org(org_uuid, username,
                                                                           payload['transaction_hash'], payload['wallet_address'])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_all_org(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    response = OrganizationService().get_organizations_for_user(username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def get_org(event, context):
    pass


def get_all_groups_for_org(event, context):
    pass


def add_group_draft_for_org(event, context):
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    required_keys = ["name", "id", "payment_address", "payment_config"]
    if "org_id" not in path_parameters and validate_dict_list(payload, required_keys):
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    response = OrganizationService().add_group(payload, org_uuid, username)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def get_group_for_org(event, context):
    pass
