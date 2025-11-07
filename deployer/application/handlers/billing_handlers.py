from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.schemas.billing_schemas import (
    GetMetricsRequest,
    CallEventConsumerRequest,
    SaveEVMTransactionRequest,
    CreateOrderRequest,
    GetBalanceHistoryRequest,
    GetBalanceAndRateRequest,
)
from deployer.application.services.authorization_service import AuthorizationService
from deployer.application.services.billing_service import BillingService
from deployer.application.services.metrics_service import MetricsService


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

    AuthorizationService().check_local_access(req_ctx.account_id, order_id=request.order_id)

    response = BillingService().save_evm_transaction(request)

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

    request = GetBalanceHistoryRequest.validate_event(event)

    response = BillingService().get_balance_history(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_metrics(event, context):
    req_ctx = RequestContext(event)

    request = GetMetricsRequest.validate_event(event)

    AuthorizationService().check_local_access(
        req_ctx.account_id, hosted_service_id=request.hosted_service_id
    )

    response = MetricsService().get_metrics(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_balance_and_rate(event, context):
    request = GetBalanceAndRateRequest.validate_event(event)

    response = BillingService().get_balance_and_rate(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def update_transaction_status(event, context):
    BillingService().update_transaction_status()
    return {}


def call_event_consumer(event, context):
    events = CallEventConsumerRequest.get_events_from_queue(event)

    for e in events:
        request = CallEventConsumerRequest.validate_event(e)
        BillingService().process_call_event(request)

    return {}


def update_token_rate(event, context):
    BillingService().update_token_rate()
    return {}
