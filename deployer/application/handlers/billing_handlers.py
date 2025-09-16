from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.schemas.billing_schemas import CreateOrderRequest
from deployer.application.schemas.order_schemas import InitiateOrderRequest
from deployer.application.schemas.transaction_schemas import SaveEVMTransactionRequest
from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.services.billing_service import BillingService
from deployer.application.services.order_service import OrderService
from deployer.application.services.transaction_service import TransactionService


logger = get_logger(__name__)


@exception_handler(logger=logger)
def create_order(event, context):
    req_ctx = RequestContext(event)

    request = CreateOrderRequest.validate_event(event)

    response = BillingService().create_order(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def save_evm_transaction(event, context):
    req_ctx = RequestContext(event)

    request = SaveEVMTransactionRequest.validate_event(event)

    AuthorizationService().check_access(req_ctx.account_id, order_id=request.order_id)

    response = TransactionService().save_evm_transaction(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_balance(event, context):
    req_ctx = RequestContext(event)

    response = BillingService().get_balance(req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_balance_history(event, context):
    req_ctx = RequestContext(event)

    response = BillingService().get_balance_history(req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_metrics(event, context):
    req_ctx = RequestContext(event)



    response = BillingService().get_metrics()

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def update_transaction_status(event, context):
    BillingService().update_transaction_status()
    return {}


def call_event_consumer(event, context):
    BillingService().process_call_event()
    return {}