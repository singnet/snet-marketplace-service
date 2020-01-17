import json

from common.constant import StatusCode
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import generate_lambda_response, handle_exception_with_slack_notification, validate_dict, \
    validate_dict_list
from registry.application.services.organization_publisher_service import OrganizationService
from registry.config import NETWORK_ID, SLACK_HOOK
from registry.constants import PostOrganizationActions

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def add_org(event, context):
    payload = json.loads(event["body"])
    action = event["queryStringParameters"]["action"]
    required_keys = ["org_id", "org_uuid", "org_name", "origin", "org_type", "metadata_ipfs_hash", "description",
                     "short_description", "url", "contacts", "assets", "mail_address_same_hq_address",
                     "addresses", "duns_no", "owner_name"]

    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    org_service = OrganizationService("", username)
    if action == PostOrganizationActions.DRAFT.value:
        response = org_service.add_organization_draft(payload)
    elif action == PostOrganizationActions.SUBMIT.value:
        response = org_service.submit_org_for_approval(payload)
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
    response = OrganizationService(org_uuid, username).publish_org_to_ipfs()

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
    response = OrganizationService(org_uuid, username).save_transaction_hash_for_publish_org(
        payload['transaction_hash'],
        payload['wallet_address'])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_all_org(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    response = OrganizationService("", username).get_organizations_for_user()

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
    response = OrganizationService(org_uuid, username).add_group(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def get_group_for_org(event, context):
    pass


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_member(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    org_uuid = path_parameters["org_id"]
    member_username = path_parameters["username"]
    response = OrganizationService(org_uuid, username).get_member(member_username)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_all_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    query_parameters = event["queryStringParameters"]
    if "org_id" not in path_parameters or "status" not in query_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    status = query_parameters["status"]
    response = OrganizationService(org_uuid, username).get_all_members(org_uuid, status, query_parameters)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def invite_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]
    if "org_id" not in path_parameters or "members" not in payload:
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    org_members = payload["members"]
    response = OrganizationService(org_uuid, username).invite_members(org_members)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def verify_code(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_string_parameters = event["queryStringParameters"]
    if "invite_code" not in query_string_parameters:
        raise BadRequestException()
    invite_code = query_string_parameters["invite_code"]
    response = OrganizationService(None, username).verify_invite(invite_code)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def publish_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]

    if "org_id" not in path_parameters or not validate_dict(payload, ["transaction_hash", "members"]):
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    transaction_hash = payload["transaction_hash"]
    org_members = payload["members"]
    response = OrganizationService(org_uuid, username).publish_members(transaction_hash, org_members)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def delete_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]
    if "org_id" not in path_parameters or "members" not in payload:
        raise BadRequestException()
    org_uuid = path_parameters["org_id"]
    org_members = payload["members"]
    response = OrganizationService(org_uuid, username).delete_members(org_members)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def register_member(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    if "invite_code" not in payload and "wallet_address" not in payload:
        raise BadRequestException()
    invite_code = payload["invite_code"]
    wallet_address = payload["wallet_address"]
    org_publisher_service = OrganizationService(None, username).compute_org_uuid_for_given_username_and_invite_code(invite_code)
    response = org_publisher_service.register_member(wallet_address)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
