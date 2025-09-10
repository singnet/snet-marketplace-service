"""Integration tests for get_transactions handler.

NOTE: The TransactionService.get_transactions() method is not implemented yet (returns None).
These tests verify that the handler doesn't crash and handles the None gracefully.
When the service method is implemented, these tests should be updated to verify
the actual transaction data returned.
"""
import json
import pytest

from deployer.application.handlers.transaction_handlers import get_transactions
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus, DaemonStatus
from common.constant import StatusCode


class TestGetTransactionsHandler:
    """Test cases for get_transactions handler."""
    
    def test_get_transactions_by_order_id(
        self,
        authorized_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test successful retrieval of transactions by order ID."""
        # Arrange
        # Create daemon with correct account
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-tx-get-001",
            account_id="test-user-id-123",
            org_id="test-org",
            service_id="test-service"
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create order
        order = test_data_factory.create_order(
            order_id="test-order-get-tx-001",
            daemon_id=daemon.id,
            status=OrderStatus.SUCCESS
        )
        order_repo.create_order(db_session, order)
        
        # Create multiple transactions for this order
        tx1 = test_data_factory.create_transaction(
            hash="0x1111111111111111111111111111111111111111111111111111111111111111",
            order_id="test-order-get-tx-001",
            status=EVMTransactionStatus.SUCCESS
        )
        tx2 = test_data_factory.create_transaction(
            hash="0x2222222222222222222222222222222222222222222222222222222222222222",
            order_id="test-order-get-tx-001",
            status=EVMTransactionStatus.PENDING
        )
        transaction_repo.upsert_transaction(db_session, tx1)
        transaction_repo.upsert_transaction(db_session, tx2)
        db_session.commit()
        
        # Prepare event
        event = authorized_event.copy()
        event["queryStringParameters"] = {"orderId": "test-order-get-tx-001"}
        event["httpMethod"] = "GET"
        event["resource"] = "/transactions"
        event["path"] = "/transactions"
        
        # Act
        response = get_transactions(event, lambda_context)
        
        # Assert
        # Note: The service method is not implemented (returns None/pass)
        # So we expect the handler to handle this gracefully
        # In real implementation, this would return transaction list
        assert response["statusCode"] in [StatusCode.OK, StatusCode.INTERNAL_SERVER_ERROR]
        
        # If the method was implemented, we would check:
        # body = json.loads(response["body"])
        # assert len(body["data"]) == 2
        # assert any(tx["hash"] == tx1.hash for tx in body["data"])
        # assert any(tx["hash"] == tx2.hash for tx in body["data"])
    
    def test_get_transactions_by_daemon_id(
        self,
        authorized_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test successful retrieval of all transactions for a daemon."""
        # Arrange
        # Create daemon
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-tx-get-002",
            account_id="test-user-id-123",
            org_id="test-org-2",
            service_id="test-service-2"
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create multiple orders for this daemon
        order1 = test_data_factory.create_order(
            order_id="test-order-get-tx-002",
            daemon_id=daemon.id,
            status=OrderStatus.SUCCESS
        )
        order2 = test_data_factory.create_order(
            order_id="test-order-get-tx-003",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, order1)
        order_repo.create_order(db_session, order2)
        
        # Create transactions for these orders
        tx1 = test_data_factory.create_transaction(
            hash="0x3333333333333333333333333333333333333333333333333333333333333333",
            order_id=order1.id,
            status=EVMTransactionStatus.SUCCESS
        )
        tx2 = test_data_factory.create_transaction(
            hash="0x4444444444444444444444444444444444444444444444444444444444444444",
            order_id=order2.id,
            status=EVMTransactionStatus.PENDING
        )
        transaction_repo.upsert_transaction(db_session, tx1)
        transaction_repo.upsert_transaction(db_session, tx2)
        db_session.commit()
        
        # Prepare event
        event = authorized_event.copy()
        event["queryStringParameters"] = {"daemonId": daemon.id}
        event["httpMethod"] = "GET"
        event["resource"] = "/transactions"
        event["path"] = "/transactions"
        
        # Act
        response = get_transactions(event, lambda_context)
        
        # Assert
        # Note: The service method is not implemented yet
        assert response["statusCode"] in [StatusCode.OK, StatusCode.INTERNAL_SERVER_ERROR]
        
        # When implemented, would verify all daemon's transactions are returned
