from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.schemas.daemon_schemas import DaemonRequest
from deployer.application.services.daemon_service import DaemonService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def get_service_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().get_service_daemon(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def get_user_daemons(event, context):
    req_ctx = RequestContext(event)

    response = DaemonService().get_user_daemons(username = req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def start_daemon_for_claiming(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().get_service_daemon(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def start_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().start_daemon(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def stop_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().stop_daemon(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def pause_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().pause_daemon(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def unpause_daemon(event, context):
    request = DaemonRequest.validate_event(event)

    response = DaemonService().unpause_daemon(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )
