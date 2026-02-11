from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response, generate_lambda_text_file_response
from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.schemas.daemon_schemas import (
    DaemonRequest,
    UpdateConfigRequest,
    UpdateDaemonStatusRequest,
)
from deployer.application.services.daemon_service import DaemonService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_daemon(event, context, daemon_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = DaemonRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(req_ctx.account_id, daemon_id=request.daemon_id)

    if daemon_service is None:
        daemon_service = DaemonService()
    response = daemon_service.get_daemon(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_daemon_logs(event, context, daemon_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = DaemonRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(req_ctx.account_id, daemon_id=request.daemon_id)

    if daemon_service is None:
        daemon_service = DaemonService()
    response = daemon_service.get_daemon_logs(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def download_daemon_logs(event, context, daemon_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = DaemonRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(req_ctx.account_id, daemon_id=request.daemon_id)

    if daemon_service is None:
        daemon_service = DaemonService()
    file_content, filename = daemon_service.download_daemon_logs(request)

    return generate_lambda_text_file_response(file_content, filename, cors_enabled=True)


@exception_handler(logger=logger)
def update_config(event, context, daemon_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = UpdateConfigRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(req_ctx.account_id, daemon_id=request.daemon_id)

    if daemon_service is None:
        daemon_service = DaemonService()
    response = daemon_service.update_config(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def update_daemon_status(event, context, daemon_service=None):
    events = UpdateDaemonStatusRequest.get_events_from_queue(event)

    if daemon_service is None:
        daemon_service = DaemonService()

    for e in events:
        request = UpdateDaemonStatusRequest.validate_event(e)
        daemon_service.update_daemon_status(request)

    return {}


@exception_handler(logger=logger)
def deploy_daemon(event, context, daemon_service=None):
    request = DaemonRequest.validate_event(event)

    if daemon_service is None:
        daemon_service = DaemonService()
    response = daemon_service.deploy_daemon(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def redeploy_all_daemons(event, context, daemon_service=None):
    if daemon_service is None:
        daemon_service = DaemonService()
    response = daemon_service.redeploy_all_daemons()

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
