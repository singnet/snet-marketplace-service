from common.constant import StatusCode
from common.exception_handler import exception_handler
from common.logger import get_logger
from common.request_context import RequestContext
from common.utils import generate_lambda_response
from deployer.application.schemas.transaction_schemas import (
    SaveEVMTransactionRequest,
    GetTransactionsRequest
)
from deployer.application.services.transaction_service import TransactionService

logger = get_logger(__name__)


@exception_handler(logger=logger)
def save_evm_transaction(event, context):
    request = SaveEVMTransactionRequest.validate_event(event)

    response = TransactionService().save_evm_transaction(request)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )


@exception_handler(logger=logger)
def get_transactions(event, context):
    req_ctx = RequestContext(event)

    request = GetTransactionsRequest.validate_event(event)

    response = TransactionService().get_transactions(request, req_ctx.username)

    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled = True
    )

