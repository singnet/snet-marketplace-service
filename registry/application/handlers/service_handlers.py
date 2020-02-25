import json

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import generate_lambda_response, handle_exception_with_slack_notification, validate_dict, \
    validate_dict_list
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.config import NETWORK_ID, SLACK_HOOK
from registry.exceptions import EXCEPTIONS

logger = get_logger(__name__)


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def verify_service_id(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    query_parameters = event["queryStringParameters"]
    if "org_uuid" not in path_parameters and "service_id" not in query_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_id = query_parameters["service_id"]
    response = ServicePublisherService(username, org_uuid, None).get_service_id_availability_status(service_id)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def save_transaction_hash_for_published_service(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).save_transaction_hash_for_published_service(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def submit_service_for_approval(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).submit_service_for_approval(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def save_service(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).save_service(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def create_service(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if "org_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    response = ServicePublisherService(username, org_uuid, None).create_service(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_services_for_organization(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if "org_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    response = ServicePublisherService(username, org_uuid, None).get_services_for_organization(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def get_service_for_service_uuid(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).get_service_for_given_service_uuid()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@handle_exception_with_slack_notification(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def publish_service_metadata_to_ipfs(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).publish_service_data_to_ipfs()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
