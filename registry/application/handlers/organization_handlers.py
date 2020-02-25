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
def get_org_for_admin(event, context):
    logger.info(event)
    query_parameters = event["queryParameters"]
    response = OrganizationPublisherService(None, None).get_for_admin(query_parameters)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_all_org(event, context):
    logger.info(event)
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    response = OrganizationPublisherService(None, username).get_all_org_for_user()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_group_for_org(event, context):
    path_parameters = event["pathParameters"]
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if "org_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    response = OrganizationPublisherService(org_uuid, username).get_groups_for_org()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def create_organization(event, context):
    payload = json.loads(event["body"])
    required_keys = []
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    response = OrganizationPublisherService(None, username).create_organization(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_org(event, context):
    payload = json.loads(event["body"])
    required_keys = []
    action = event["queryStringParameters"].get("action", None)
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if not validate_dict(payload, required_keys):
        raise BadRequestException()
    org_uuid = payload.get("org_uuid", None)
    org_service = OrganizationPublisherService(org_uuid, username)
    if action == AddOrganizationActions.DRAFT.value:
        response = org_service.save_organization_draft(payload)
    elif action == AddOrganizationActions.SUBMIT.value:
        response = org_service.submit_organization_for_approval(payload)
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
    if "org_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    response = OrganizationPublisherService(org_uuid, username).publish_org_to_ipfs()

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def save_transaction_hash_for_publish_org(event, context):
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    if "org_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    response = OrganizationPublisherService(org_uuid, username).save_transaction_hash_for_publish_org(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_all_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    query_parameters = event["queryStringParameters"]
    if "org_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    status = query_parameters.get("status", None)
    role = query_parameters.get("role", None)
    response = OrganizationPublisherService(org_uuid, username).get_all_member(status, role, query_parameters)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_member(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    org_uuid = path_parameters["org_uuid"]
    member_username = path_parameters["username"]
    response = OrganizationPublisherService(org_uuid, username).get_member(member_username)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def invite_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters or "members" not in payload:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    org_members = payload["members"]
    response = OrganizationPublisherService(org_uuid, username).invite_members(org_members)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def verify_code(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    query_string_parameters = event["queryStringParameters"]
    if "invite_code" not in query_string_parameters:
        raise BadRequestException()
    invite_code = query_string_parameters["invite_code"]
    response = OrganizationPublisherService(None, username).verify_invite(invite_code)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def publish_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]

    if "org_uuid" not in path_parameters or not validate_dict(payload, ["transaction_hash", "members"]):
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    transaction_hash = payload["transaction_hash"]
    org_members = payload["members"]
    response = OrganizationPublisherService(org_uuid, username).publish_members(transaction_hash, org_members)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def delete_members(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters or "members" not in payload:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    org_members = payload["members"]
    response = OrganizationPublisherService(org_uuid, username).delete_members(org_members)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def register_member(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    payload = json.loads(event["body"])
    if "invite_code" not in payload and "wallet_address" not in payload:
        raise BadRequestException()
    invite_code = payload["invite_code"]
    wallet_address = payload["wallet_address"]
    response = OrganizationPublisherService(None, username).register_member(invite_code, wallet_address)
    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
