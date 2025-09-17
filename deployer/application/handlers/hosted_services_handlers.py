from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.schemas.hosted_services_schemas import HostedServiceRequest, UpdateHostedServiceStatusRequest
from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.services.hosted_services_service import HostedServicesService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_hosted_service(event, context):
    req_ctx = RequestContext(event)

    request = HostedServiceRequest.validate_event(event)

    AuthorizationService().check_local_access(req_ctx.account_id, hosted_service_id=request.hosted_service_id)

    response = HostedServicesService().get_hosted_service(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_hosted_service_logs(event, context):
    req_ctx = RequestContext(event)

    request = HostedServiceRequest.validate_event(event)

    AuthorizationService().check_local_access(req_ctx.account_id, hosted_service_id=request.hosted_service_id)

    response = HostedServicesService().get_hosted_service_logs(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def update_hosted_service_status(event, context):
    events = UpdateHostedServiceStatusRequest.get_events_from_queue(event)

    for e in events:
        # TODO: we probably have to unpack the event
        request = UpdateHostedServiceStatusRequest.validate_event(e)
        HostedServicesService().update_hosted_service_status(request)

    return {}


@exception_handler(logger=logger)
def deploy_service(event, context):
    req_ctx = RequestContext(event)

    request = HostedServiceRequest.validate_event(event)

    AuthorizationService().check_local_access(req_ctx.account_id, hosted_service_id=request.hosted_service_id)

    response = HostedServicesService().deploy_service(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def delete_service(event, context):
    req_ctx = RequestContext(event)

    request = HostedServiceRequest.validate_event(event)

    AuthorizationService().check_local_access(req_ctx.account_id, hosted_service_id=request.hosted_service_id)

    response = HostedServicesService().delete_service(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )

