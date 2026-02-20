import json
from datetime import datetime
from typing import Tuple, Union, Any, Optional

from sqlalchemy.orm import Session

from common.constant import RequestPayloadType
from common.logger import get_logger
from deployer.domain.models.daemon import NewDaemonDomain
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.domain.models.transactions_metadata import NewTransactionsMetadataDomain
from deployer.infrastructure.models import (
    OrderStatus,
    EVMTransactionStatus,
    TransactionsMetadata,
    DaemonStatus,
)
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository

logger = get_logger(__name__)


def validate_response_ok(response) -> Tuple[int, Union[dict, list]]:
    assert 200 <= response["statusCode"] <= 202, "Response is not OK!"
    body = json.loads(response["body"])
    assert body["status"] == "success", "Response is not successful!"

    return response["statusCode"], body["data"]


def validate_response_bad_request(response) -> Tuple[int, str]:
    assert response["statusCode"] == 400, "Response has no BAD REQUEST error!"
    body = json.loads(response["body"])
    assert body["status"] == "failed", "Response is suddenly successful!"

    return response["statusCode"], body["error"]["message"]


def validate_response_forbidden(response) -> Tuple[int, str]:
    assert response["statusCode"] == 403, "Response has no FORBIDDEN error!"
    body = json.loads(response["body"])
    assert body["status"] == "failed", "Response is suddenly successful!"

    return response["statusCode"], body["error"]["message"]


def validate_response_not_found(response) -> Tuple[int, str]:
    assert response["statusCode"] == 404, "Response has no NOT FOUND error!"
    body = json.loads(response["body"])
    assert body["status"] == "failed", "Response is suddenly successful!"

    return response["statusCode"], body["error"]["message"]


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


def add_order(
    session: Session,
    order_id: str = "test_order_id",
    account_id: str = "SERVERLESS_OFFLINE_ACCOUNT_ID",
    amount: int = 123,
    order_status: OrderStatus = OrderStatus.PROCESSING,
) -> NewOrderDomain:
    order = NewOrderDomain(
        id=order_id,
        account_id=account_id,
        amount=amount,
        status=order_status,
    )
    OrderRepository.create_order(session, order)
    return order


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
    order = add_order(session, order_id, account_id, amount, order_status)
    transaction = NewEVMTransactionDomain(
        hash=tx_hash, order_id=order_id, status=tx_status, sender=sender, recipient=recipient
    )
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


def add_daemon(
    session: Session,
    account_id,
    org_id,
    service_id,
    daemon_id,
    status=DaemonStatus.UP,
    daemon_config=None,
    daemon_endpoint="",
    status_observed_at=None,
    status_resource_version=None,
):
    daemon = DaemonRepository.get_daemon(session, daemon_id)
    daemon_exists = daemon is not None
    if isinstance(status_observed_at, str):
        status_observed_at = datetime.fromisoformat(status_observed_at).replace(
            microsecond=0, tzinfo=None
        )
    DaemonRepository.create_daemon(
        session,
        NewDaemonDomain(
            id=daemon_id if not daemon_exists else f"{daemon_id}_2",
            account_id=account_id,
            org_id=org_id if not daemon_exists else f"{org_id}_2",
            service_id=service_id if not daemon_exists else f"{service_id}_2",
            status=status,
            daemon_config=daemon_config if daemon_config is not None else {},
            daemon_endpoint=daemon_endpoint,
            status_observed_at=status_observed_at,
            status_resource_version=status_resource_version,
        ),
    )


def create_common_queue_event(events: list) -> dict:
    return {
        "Records": [
            {"body": json.dumps({"Message": json.dumps(event_data)})} for event_data in events
        ]
    }
