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
def initiate_deployment(event, context, deployments_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = InitiateDeploymentRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_service_access(req_ctx, request.org_id)

    if deployments_service is None:
        deployments_service = DeploymentsService()
    response = deployments_service.initiate_deployment(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_user_deployments(event, context, deployments_service=None):
    req_ctx = RequestContext(event)

    if deployments_service is None:
        deployments_service = DeploymentsService()
    response = deployments_service.get_user_deployments(req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def search_deployments(event, context, deployments_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = SearchDeploymentsRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_service_access(req_ctx, request.org_id)

    if deployments_service is None:
        deployments_service = DeploymentsService()
    response = deployments_service.search_deployments(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_public_key(event, context, deployments_service=None):
    if deployments_service is None:
        deployments_service = DeploymentsService()
    response = deployments_service.get_public_key()

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def registry_event_consumer(event, context, deployments_service=None):
    events = RegistryEventConsumerRequest.get_events_from_queue(event)

    if deployments_service is None:
        deployments_service = DeploymentsService()

    for e in events:
        request = RegistryEventConsumerRequest.validate_event(e["blockchain_event"])
        if request.event_name in ["ServiceCreated", "ServiceMetadataModified", "ServiceDeleted"]:
            deployments_service.process_registry_event(request)

    return {}
