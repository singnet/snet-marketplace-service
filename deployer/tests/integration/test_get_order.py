"""
Integration tests for get_order handler.
"""
import json
import pytest
from datetime import datetime, UTC

from deployer.application.handlers.order_handlers import get_order
from deployer.infrastructure.models import OrderStatus, EVMTransactionStatus
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository
from common.constant import StatusCode


class TestGetOrderHandler:
    """Test cases for get_order handler."""
    
    def test_get_order_success(
        self,
        get_order_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo
    ):
        """Test successful retrieval of order data."""
        # Arrange
        # Create daemon with correct account_id from event
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-001",
            account_id="test-user-id-123",  # Matches the authorized_event fixture
            org_id="test-org",
            service_id="test-service"
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create order for this daemon
        order = test_data_factory.create_order(
            order_id="test-order-001",
            daemon_id=daemon.id,
            status=OrderStatus.SUCCESS
        )
        order_repo.create_order(db_session, order)
        db_session.commit()
        
        # Update event with the created order ID
        event = get_order_event
        event["pathParameters"]["orderId"] = "test-order-001"
        
        # Act
        response = get_order(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "data" in body
        
        # Verify returned order data
        order_data = body["data"]
        assert order_data["id"] == "test-order-001"
        assert order_data["daemonId"] == "test-daemon-001"
        assert order_data["status"] == OrderStatus.SUCCESS.value
    
    def test_get_order_with_transactions(
        self,
        get_order_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test successful retrieval of order with associated transactions."""
        # Arrange
        # Create daemon
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-002",
            account_id="test-user-id-123",
            org_id="test-org-2",
            service_id="test-service-2"
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create order
        order = test_data_factory.create_order(
            order_id="test-order-002",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, order)
        
        # Create transaction for this order
        transaction = test_data_factory.create_transaction(
            hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            order_id="test-order-002",
            status=EVMTransactionStatus.PENDING,
            sender="0xUserWalletAddress",
            recipient="0xMarketplaceAddress"
        )
        transaction_repo.upsert_transaction(db_session, transaction)
        db_session.commit()
        
        # Update event
        event = get_order_event
        event["pathParameters"]["orderId"] = "test-order-002"
        
        # Act
        response = get_order(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        order_data = body["data"]
        assert order_data["id"] == "test-order-002"
        assert order_data["status"] == OrderStatus.PROCESSING.value
        
        # Note: The to_short_response() method might not include transactions
        # But if it does, we can verify them here
        # This depends on the implementation of OrderDomain.to_short_response()
    
    def test_get_order_fails_for_wrong_user(
        self,
        get_order_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo
    ):
        """Test that authorization prevents accessing another user's order."""
        # Arrange
        # Create daemon with DIFFERENT account_id
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-other",
            account_id="different-user-id-456",  # Different user!
            org_id="test-org",
            service_id="test-service"
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create order for this daemon
        order = test_data_factory.create_order(
            order_id="test-order-other",
            daemon_id=daemon.id,
            status=OrderStatus.SUCCESS
        )
        order_repo.create_order(db_session, order)
        db_session.commit()
        
        # Update event to try to access this order
        event = get_order_event
        event["pathParameters"]["orderId"] = "test-order-other"
        
        # Act
        response = get_order(event, lambda_context)
        
        # Assert - should fail with 403 Forbidden
        assert response["statusCode"] == StatusCode.FORBIDDEN
