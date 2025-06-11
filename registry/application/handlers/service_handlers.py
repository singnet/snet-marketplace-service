from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.exceptions import BadRequestException
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict
from registry.application.access_control.authorization import secured
from registry.application.services.service_publisher_service import ServicePublisherService
from registry.application.services.service_transaction_status import ServiceTransactionStatus
from registry.config import NETWORK_ID, SLACK_HOOK
from registry.constants import Action
from registry.exceptions import EXCEPTIONS
from registry.application.services.update_service_assets import UpdateServiceAssets
from common.request_context import RequestContext

from registry.application.schemas.service import (
    CreateServiceRequest,
    GetCodeBuildStatusRequest,
    GetDaemonConfigRequest,
    GetServiceRequest,
    GetServicesForOrganizationRequest,
    SaveServiceGroupsRequest,
    ServiceDeploymentStatusRequest,
    VerifyServiceIdRequest,
    SaveTransactionHashRequest,
    SaveServiceRequest,
    PublishServiceRequest,
)
from common.schemas import PayloadValidationError

logger = get_logger(__name__)


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def verify_service_id(event, context):
    request = VerifyServiceIdRequest.validate_event(event)

    response = ServicePublisherService().get_service_id_availability_status(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def save_transaction_hash_for_published_service(event, context):
    req_context = RequestContext(event)

    request = SaveTransactionHashRequest.validate_event(event)

    response = ServicePublisherService().save_transaction_hash_for_published_service(
        req_context.username, request
    )

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def save_service(event, context):
    req_ctx = RequestContext(event)

    request = SaveServiceRequest.validate_event(event)
        
    response = ServicePublisherService().save_service(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def save_service_attributes(event, context):
    req_ctx = RequestContext(event)

    request = SaveServiceGroupsRequest.validate_event(event)

    response = ServicePublisherService().save_service_groups(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def create_service(event, context):
    req_ctx = RequestContext(event)

    request = CreateServiceRequest.validate_event(event)

    response = ServicePublisherService().create_service(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def get_services_for_organization(event, context):
    request = GetServicesForOrganizationRequest.validate_event(event)

    response = ServicePublisherService().get_services_for_organization(request)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def get_service_for_service_uuid(event, context):
    
    request = GetServiceRequest.validate_event(event)
    
    response = ServicePublisherService().get_service_for_given_service_uuid(
        request.org_uuid, request.service_uuid
    )

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(NETWORK_ID=NETWORK_ID, logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def get_daemon_config_for_current_network(event, context):
    request = GetDaemonConfigRequest.validate_event(event)

    response = ServicePublisherService().daemon_config(request)   

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
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


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def service_deployment_status_notification_handler(event, context):
    req_ctx = RequestContext(event)

    request = ServiceDeploymentStatusRequest.validate_event(event)
    
    ServicePublisherService().service_build_status_notifier(req_ctx.username, request)

    return generate_lambda_response(
        StatusCode.CREATED,
        {"status": "success", "data": "Build failure notified", "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_transaction(event, context):
    logger.info(f"Update transaction event :: {event}")
    ServiceTransactionStatus().update_transaction_status()
    return generate_lambda_response(StatusCode.OK, "OK")


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def get_code_build_status_for_service(event, context):
    request = GetCodeBuildStatusRequest.validate_event(event)

    response = ServicePublisherService().get_service_demo_component_build_status(request)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_service_assets(event, context):
    logger.info(f"Update service assets event :: {event}")
    response = UpdateServiceAssets().validate_and_process_service_assets(payload=event)
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )

@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
def update_demo_component_build_status(event, context):
    org_uuid = event['org_uuid']
    service_uuid = event['service_uuid']
    build_status = event['build_status']
    build_id = event['build_id']
    filename = event['filename']
    response = UpdateServiceAssets().update_demo_component_build_status(
        org_uuid=org_uuid,
        service_uuid=service_uuid,
        build_status=build_status,
        build_id=build_id,
        filename=filename
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )

@exception_handler(logger=logger, EXCEPTIONS=EXCEPTIONS)
@secured(action=Action.CREATE, org_uuid_path=("pathParameters", "org_uuid"),
         username_path=("requestContext", "authorizer", "claims", "email"))
def publish_service(event, context):
    req_ctx = RequestContext(event)
    
    request = PublishServiceRequest.validate_event(event)

    response = ServicePublisherService(request.lighthouse_token).publish_service(
        req_ctx.username, request
    )
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )