from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response, generate_lambda_text_file_response
from deployer.application.schemas.hosted_services_schemas import (
    HostedServiceRequest,
    UpdateHostedServiceStatusRequest,
    CheckGithubRepositoryRequest,
)
from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.services.hosted_services_service import HostedServicesService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_hosted_service(event, context, hosted_services_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = HostedServiceRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(
        req_ctx.account_id, hosted_service_id=request.hosted_service_id
    )

    if hosted_services_service is None:
        hosted_services_service = HostedServicesService()
    response = hosted_services_service.get_hosted_service(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def check_github_repository(event, context, hosted_services_service=None):
    request = CheckGithubRepositoryRequest.validate_event(event)

    if hosted_services_service is None:
        hosted_services_service = HostedServicesService()
    response = hosted_services_service.check_github_repository(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_hosted_service_logs(event, context, hosted_services_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = HostedServiceRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(
        req_ctx.account_id, hosted_service_id=request.hosted_service_id
    )

    if hosted_services_service is None:
        hosted_services_service = HostedServicesService()
    response = hosted_services_service.get_hosted_service_logs(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def download_hosted_service_logs(event, context, hosted_services_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = HostedServiceRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(
        req_ctx.account_id, hosted_service_id=request.hosted_service_id
    )

    if hosted_services_service is None:
        hosted_services_service = HostedServicesService()
    file_content, filename = hosted_services_service.download_hosted_service_logs(request)

    return generate_lambda_text_file_response(file_content, filename, cors_enabled=True)


def update_hosted_service_status(event, context, hosted_services_service=None):
    events = UpdateHostedServiceStatusRequest.get_events_from_queue(event)

    if hosted_services_service is None:
        hosted_services_service = HostedServicesService()

    for e in events:
        request = UpdateHostedServiceStatusRequest.validate_event(e)
        hosted_services_service.update_hosted_service_status(request)

    return {}
