from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.handlers.authorization import AuthorizationHandler
from deployer.application.schemas.order_schemas import InitiateOrderRequest, GetOrderRequest
from deployer.application.services.order_service import OrderService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def initiate_order(event, context):
    req_ctx = RequestContext(event)

    request = InitiateOrderRequest.validate_event(event)

    response = OrderService().initiate_order(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def get_order(event, context):
    req_ctx = RequestContext(event)

    request = GetOrderRequest.validate_event(event)

    AuthorizationHandler().check_access(req_ctx.account_id, order_id = request.order_id)

    response = OrderService().get_order(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )

