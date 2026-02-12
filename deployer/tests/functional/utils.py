import json
from typing import Tuple, Union, Any, Optional

from sqlalchemy.orm import Session

from common.constant import RequestPayloadType
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.domain.models.transactions_metadata import NewTransactionsMetadataDomain
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus, TransactionsMetadata
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository


def validate_response_ok(response) -> Tuple[int, Union[dict, list]]:
    assert 200 <= response["statusCode"] <= 202, "Response is not OK!"
    body = json.loads(response["body"])
    assert body["status"] == "success", "Response is not successful!"

    return response["statusCode"], body["data"]


def validate_response_bad_request(response) -> Tuple[int, str]:
    assert response["statusCode"] == 400, "Response has no BAD REQUEST error!"
    body = json.loads(response["body"])
    assert body["status"] == "failed", "Response is suddenly successful!"

    return response["statusCode"], body["message"]


def validate_response_server_error(response) -> Union[dict, Any]:
    assert response["statusCode"] == 500, "Response has no INTERNAL SERVER ERROR!"
    body = json.loads(response["body"])
    assert body["status"] == "failed", "Response is suddenly successful!"
    assert body["message"] == "Unexpected server error"

    return body["details"]


def generate_request_event(
    path_parameters: Optional[dict] = None,
    query_parameters: Optional[dict] = None,
    body: Optional[dict] = None,
    **kwargs,
) -> dict:
    event = {}

    if path_parameters is not None:
        event[RequestPayloadType.PATH_PARAMS] = path_parameters
    if query_parameters is not None:
        event[RequestPayloadType.QUERY_STRING] = query_parameters
    if body is not None:
        event[RequestPayloadType.BODY] = json.dumps(body)
    event.update(**kwargs)

    return event


def create_order_and_transaction(
    session: Session,
    order_id: str = "test_order_id",
    account_id: str = "test_account_id",
    amount: int = 123,
    order_status: OrderStatus = OrderStatus.PROCESSING,
    tx_hash: str = "0x123",
    tx_status: EVMTransactionStatus = EVMTransactionStatus.PENDING,
    sender: str = "0xsender",
    recipient: str = "0xrecipient",
) -> Tuple[NewOrderDomain, NewEVMTransactionDomain]:
    order = NewOrderDomain(
        id=order_id,
        account_id=account_id,
        amount=amount,
        status=order_status,
    )
    transaction = NewEVMTransactionDomain(
        hash=tx_hash, order_id=order_id, status=tx_status, sender=sender, recipient=recipient
    )

    OrderRepository.create_order(session, order)
    TransactionRepository.upsert_transaction(session, transaction)

    return order, transaction


def add_transactions_metadata(
    session: Session,
    last_block_no: int = 900,
    transactions_metadata: Optional[NewTransactionsMetadataDomain] = None,
) -> NewTransactionsMetadataDomain:
    if transactions_metadata is None:
        transactions_metadata = NewTransactionsMetadataDomain(
            id=123,
            recipient="recipient",
            last_block_no=last_block_no,
            fetch_limit=50,
            block_adjustment=5,
        )

    session.add(
        TransactionsMetadata(
            id=transactions_metadata.id,
            recipient=transactions_metadata.recipient,
            last_block_no=transactions_metadata.last_block_no,
            fetch_limit=transactions_metadata.fetch_limit,
            block_adjustment=transactions_metadata.block_adjustment,
        )
    )
    return transactions_metadata


def create_common_queue_event(events: list) -> dict:
    return {
        "Records": [
            {"body": json.dumps({"Message": json.dumps(event_data)})} for event_data in events
        ]
    }
