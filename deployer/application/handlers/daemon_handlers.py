from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.schemas.daemon_schemas import (
    DaemonRequest,
    UpdateConfigRequest,
    SearchDaemonRequest, UpdateDaemonStatusRequest,
)
from deployer.application.services.daemon_service import DaemonService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_daemon(event, context):
    req_ctx = RequestContext(event)

    request = DaemonRequest.validate_event(event)

    AuthorizationService().check_local_access(req_ctx.account_id, daemon_id=request.daemon_id)

    response = DaemonService().get_daemon(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_daemon_logs(event, context):
    req_ctx = RequestContext(event)

    request = DaemonRequest.validate_event(event)

    AuthorizationService().check_local_access(req_ctx.account_id, daemon_id=request.daemon_id)

    response = DaemonService().get_daemon_logs(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def update_config(event, context):
    req_ctx = RequestContext(event)

    request = UpdateConfigRequest.validate_event(event)

    AuthorizationService().check_local_access(req_ctx.account_id, daemon_id=request.daemon_id)

    response = DaemonService().update_config(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def update_daemon_status(event, context):
    events = UpdateDaemonStatusRequest.get_events_from_queue(event)

    for e in events:
        # TODO: we probably have to unpack the event
        request = UpdateDaemonStatusRequest.validate_event(e)
        DaemonService().update_daemon_status(request)

    return {}


@exception_handler(logger=logger)
def start_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().start_daemon(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def stop_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().stop_daemon(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )

@exception_handler(logger=logger)
def redeploy_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().redeploy_daemon(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def redeploy_all_daemons(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().redeploy_all_daemons(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
