import sys
sys.path.append('/opt')
import json

from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from registry.application.access_control.authorization import secured
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.application.services.service_transaction_status import ServiceTransactionStatus
from registry.config import NETWORK_ID, SLACK_HOOK
from registry.constants import Action, EnvironmentType
from registry.exceptions import EnvironmentNotFoundException, EXCEPTIONS
from registry.application.services.update_service_assets import UpdateServiceAssets

logger = get_logger(__name__)


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def save_service(event, context):
    logger.info(f"Event for save service {event}")
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if not path_parameters.get("org_uuid") and not path_parameters.get("service_uuid"):
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
def save_service_attributes(event, context):
    logger.info(f"Event for save service {event}")
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    payload = json.loads(event["body"])
    if not path_parameters.get("org_uuid", "") and not path_parameters.get("service_uuid", ""):
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(username, org_uuid, service_uuid).save_service_attributes(payload)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
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


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def publish_service_metadata_to_ipfs(event, context):
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters and \
        "service_uuid" not in path_parameters and "provider_storage" not in path_parameters:
        raise BadRequestException()
    response = ServicePublisherService(
        username,
        path_parameters["org_uuid"],
        path_parameters["service_uuid"]
    ).publish_service_data_to_ipfs()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def get_daemon_config_for_current_network(event, context):
    logger.info(f"event for get_daemon_config_for_current_network:: {event}")
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    query_parameters = event["queryStringParameters"]
    if not validate_dict(path_parameters,
                         ["org_uuid", "service_uuid", "group_id"]) or 'network' not in query_parameters:
        raise BadRequestException()
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    if query_parameters["network"] == EnvironmentType.TEST.value:
        response = ServicePublisherService(username, org_uuid, service_uuid).daemon_config(
            environment=EnvironmentType.TEST.value)
    elif query_parameters["network"] == EnvironmentType.MAIN.value:
        response = ServicePublisherService(username, org_uuid, service_uuid).daemon_config(
            environment=EnvironmentType.MAIN.value)
    else:
        raise EnvironmentNotFoundException()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_service_details_using_org_id_service_id(event, context):
    logger.info(f"event: {event}")
    query_parameters = event["queryStringParameters"]
    if not validate_dict(query_parameters, ["org_id", "service_id"]):
        raise BadRequestException()
    org_id = query_parameters["org_id"]
    service_id = query_parameters["service_id"]
    response = ServicePublisherService.get_service_for_org_id_and_service_id(org_id, service_id)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def service_deployment_status_notification_handler(event, context):
    logger.info(f"Service Build status event {event}")
    org_id = event['org_id']
    service_id = event['service_id']
    build_status = int(event['build_status'])

    ServicePublisherService("BUILD_PROCESS", "", "").service_build_status_notifier(org_id, service_id, build_status)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": "Build failure notified", "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_transaction(event, context):
    logger.info(f"Update transaction event :: {event}")
    ServiceTransactionStatus().update_transaction_status()
    return generate_lambda_response(StatusCode.OK, "OK")


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_code_build_status_for_service(event, context):
    logger.info(f"Get code build status event :: {event}")
    path_parameters = event["pathParameters"]
    org_uuid = path_parameters["org_uuid"]
    service_uuid = path_parameters["service_uuid"]
    response = ServicePublisherService(org_uuid=org_uuid, service_uuid=service_uuid, username=None) \
        .get_service_demo_component_build_status()
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_service_assets(event, context):
    logger.info(f"Update service assets event :: {event}")
    response = UpdateServiceAssets().validate_and_process_service_assets(payload=event)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )

@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_demo_component_build_status(event, context):
    logger.info(f"Demo component build status update event :: {event}")
    org_uuid = event['org_uuid']
    service_uuid = event['service_uuid']
    build_status = event['build_status']
    build_id = event['build_id']
    filename = event['filename']
    response = UpdateServiceAssets()\
        .update_demo_component_build_status(org_uuid=org_uuid, service_uuid=service_uuid,
                                            build_status=build_status, build_id=build_id,
                                            filename=filename)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )

@exception_handler(SLACK_HOOK=SLACK_HOOK, NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def publish_service(event, context):
    logger.info(f"Publish service event::{event}")
    username = event["requestContext"]["authorizer"]["claims"]["email"]
    path_parameters = event["pathParameters"]
    if "org_uuid" not in path_parameters and \
        "service_uuid" not in path_parameters and "provider_storage" not in path_parameters:
        raise BadRequestException()
    response = ServicePublisherService(
        username,
        path_parameters["org_uuid"],
        path_parameters["service_uuid"]
    ).publish_service(path_parameters["provider_storage"])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )