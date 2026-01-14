from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.schemas.deployments_schemas import (
    InitiateDeploymentRequest,
    SearchDeploymentsRequest,
    RegistryEventConsumerRequest,
)
from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.services.deployments_service import DeploymentsService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def initiate_deployment(event, context):
    req_ctx = RequestContext(event)

    request = InitiateDeploymentRequest.validate_event(event)

    AuthorizationService().check_service_access(req_ctx, request.org_id)

    response = DeploymentsService().initiate_deployment(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_user_deployments(event, context):
    req_ctx = RequestContext(event)

    response = DeploymentsService().get_user_deployments(req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def search_deployments(event, context):
    req_ctx = RequestContext(event)

    request = SearchDeploymentsRequest.validate_event(event)

    AuthorizationService().check_service_access(req_ctx, request.org_id)

    response = DeploymentsService().search_deployments(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_public_key(event, context):
    response = DeploymentsService().get_public_key()

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def registry_event_consumer(event, context):
    events = RegistryEventConsumerRequest.get_events_from_queue(event)

    for e in events:
        request = RegistryEventConsumerRequest.validate_event(e["blockchain_event"])
        if request.event_name in ["ServiceCreated", "ServiceMetadataModified", "ServiceDeleted"]:
            DeploymentsService().process_registry_event(request)

    return {}
