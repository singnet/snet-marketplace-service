import json

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import generate_lambda_response
from registry.application.access_control.authorization import secured
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.config import NETWORK_ID, SLACK_HOOK
from registry.constants import EnvironmentType, Action
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def save_transaction_hash_for_published_service(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).save_transaction_hash_for_published_service(
        payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def submit_service_for_approval(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if not path_parameters.get("org_uuid", "") and not path_parameters.get("service_uuid", ""):
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).submit_service_for_approval(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def save_service(event, context):
    logger.info(f"Event for save service {event}")
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if not path_parameters.get("org_uuid", "") and not path_parameters.get("service_uuid", ""):
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).save_service(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def create_service(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if not path_parameters.get("org_uuid", ""):
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    response = ServicePublisherService(username, org_uuid, None).create_service(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def legal_approval_of_service(event, context):
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(None, org_uuid, service_uuid).approve_service()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def list_of_service_pending_for_approval_from_slack(event, context):
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    response = ServicePublisherService(None, org_uuid, None).get_list_of_service_pending_for_approval()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
def list_of_orgs_with_services_submitted_for_approval(event, context):
    response = ServicePublisherService(None, None, None).get_list_of_orgs_with_services_submitted_for_approval()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def get_daemon_config_for_test(event, context):
    logger.info(f"event for get_daemon_config_for_test:: {event}")
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters and "group_id" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    group_id = path_parameters["group_id"]
    response = ServicePublisherService(username, org_uuid, service_uuid).daemon_config(environment=EnvironmentType.TEST.value)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def get_daemon_config_for_current_network(event, context):
    logger.info(f"event for get_daemon_config_for_current_network:: {event}")
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters and "service_uuid" not in path_parameters and "group_id" not in path_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    group_id = path_parameters["group_id"]
    response = ServicePublisherService(username, org_uuid, service_uuid).daemon_config(environment=EnvironmentType.MAIN.value)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def get_service_details_using_org_id_service_id(event, context):
    logger.info(f"event for get_daemon_config_for_current_network:: {event}")
    path_parameters = event["queryStringParameters"]
    org_id = path_parameters["org_id"]
    service_id = path_parameters["service_id"]
    org_uuid, service = ServicePublisherRepository().get_service_for_given_service_id_and_org_id(org_id, service_id)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": service.to_dict(), "error": {}}, cors_enabled=True
    )


def service_deployment_status_notification_handler(event,context):
    logger.info(f"Service Build status event {event}")
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": "chill", "error": {}}, cors_enabled=True
    )

