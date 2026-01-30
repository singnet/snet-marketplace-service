from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response, generate_lambda_text_file_response
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
def create_order(event, context, billing_service=None):
    req_ctx = RequestContext(event)

    request = CreateOrderRequest.validate_event(event)

    if billing_service is None:
        billing_service = BillingService()
    response = billing_service.create_order(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def save_evm_transaction(event, context, billing_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = SaveEVMTransactionRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(req_ctx.account_id, order_id=request.order_id)

    if billing_service is None:
        billing_service = BillingService()
    response = billing_service.save_evm_transaction(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_balance(event, context, billing_service=None):
    req_ctx = RequestContext(event)

    if billing_service is None:
        billing_service = BillingService()
    response = billing_service.get_balance(req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_balance_history(event, context, billing_service=None):
    req_ctx = RequestContext(event)

    request = GetBalanceHistoryRequest.validate_event(event)

    if billing_service is None:
        billing_service = BillingService()
    response = billing_service.get_balance_history(request, req_ctx.account_id)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def get_metrics(event, context, metrics_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = GetMetricsRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(req_ctx.account_id, hosted_service_id=request.hosted_service_id)

    if metrics_service is None:
        metrics_service = MetricsService()
    response = metrics_service.get_metrics(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


@exception_handler(logger=logger)
def download_metrics(event, context, metrics_service=None, auth_service=None):
    req_ctx = RequestContext(event)

    request = GetMetricsRequest.validate_event(event)

    if auth_service is None:
        auth_service = AuthorizationService()
    auth_service.check_local_access(req_ctx.account_id, hosted_service_id=request.hosted_service_id)

    if metrics_service is None:
        metrics_service = MetricsService()
    file_content, filename = metrics_service.download_metrics(request)

    return generate_lambda_text_file_response(file_content, filename, cors_enabled=True)


@exception_handler(logger=logger)
def get_balance_and_rate(event, context, billing_service=None):
    request = GetBalanceAndRateRequest.validate_event(event)

    if billing_service is None:
        billing_service = BillingService()
    response = billing_service.get_balance_and_rate(request)

    return generate_lambda_response(
        StatusCode.OK, {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )


def update_transaction_status(event, context, billing_service=None):
    if billing_service is None:
        billing_service = BillingService()
    billing_service.update_transaction_status()

    return {}


def call_event_consumer(event, context, billing_service=None):
    events = CallEventConsumerRequest.get_events_from_queue(event)

    if billing_service is None:
        billing_service = BillingService()

    for e in events:
        request = CallEventConsumerRequest.validate_event(e)
        billing_service.process_call_event(request)

    return {}


def update_token_rate(event, context, billing_service=None):
    if billing_service is None:
        billing_service = BillingService()
    billing_service.update_token_rate()

    return {}
