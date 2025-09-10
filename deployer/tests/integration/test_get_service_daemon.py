"""
Integration tests for get_service_daemon handler.
"""
import json
import pytest

from deployer.application.handlers.daemon_handlers import get_service_daemon
from deployer.infrastructure.models import DaemonStatus, OrderStatus, EVMTransactionStatus
from common.constant import StatusCode


class TestGetServiceDaemonHandler:
    """Test cases for get_service_daemon handler.
    
    This handler returns full daemon information including:
    - Daemon details (without accountId for privacy)
    - All orders for the daemon
    - All transactions for each order
    - Daemon configuration
    """
    
    def test_get_service_daemon_success(
        self,
        authorized_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        transaction_repo
    ):
        """Test successful retrieval of daemon with all its orders and transactions."""
        # Arrange
        # Create daemon with correct account_id
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-full-001",
            account_id="test-user-id-123",  # Matches authorized user
            org_id="test-org-full",
            service_id="test-service-full",
            status=DaemonStatus.UP
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create multiple orders for this daemon
        order1 = test_data_factory.create_order(
            order_id="test-order-full-001",
            daemon_id=daemon.id,
            status=OrderStatus.SUCCESS
        )
        order2 = test_data_factory.create_order(
            order_id="test-order-full-002",
            daemon_id=daemon.id,
            status=OrderStatus.PROCESSING
        )
        order3 = test_data_factory.create_order(
            order_id="test-order-full-003",
            daemon_id=daemon.id,
            status=OrderStatus.FAILED
        )
        order_repo.create_order(db_session, order1)
        order_repo.create_order(db_session, order2)
        order_repo.create_order(db_session, order3)
        
        # Create transactions for some orders
        tx1 = test_data_factory.create_transaction(
            hash="0xaaaa1111111111111111111111111111111111111111111111111111111111aa",
            order_id=order1.id,
            status=EVMTransactionStatus.SUCCESS
        )
        tx2 = test_data_factory.create_transaction(
            hash="0xbbbb2222222222222222222222222222222222222222222222222222222222bb",
            order_id=order2.id,
            status=EVMTransactionStatus.PENDING
        )
        transaction_repo.upsert_transaction(db_session, tx1)
        transaction_repo.upsert_transaction(db_session, tx2)
        db_session.commit()
        
        # Prepare event
        event = authorized_event.copy()
        event["pathParameters"] = {"daemonId": daemon.id}
        event["httpMethod"] = "GET"
        event["resource"] = "/daemon/{daemonId}"
        event["path"] = f"/daemon/{daemon.id}"
        
        # Act
        response = get_service_daemon(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "data" in body
        
        # Verify daemon data
        daemon_data = body["data"]
        assert daemon_data["id"] == daemon.id
        assert daemon_data["orgId"] == "test-org-full"
        assert daemon_data["serviceId"] == "test-service-full"
        assert daemon_data["status"] == DaemonStatus.UP.value
        assert "accountId" not in daemon_data  # accountId is removed in to_response()
        assert daemon_data["daemonEndpoint"] == daemon.daemon_endpoint
        assert daemon_data["servicePublished"] == False
        assert "daemonConfig" in daemon_data
        assert daemon_data["startAt"] is not None
        assert daemon_data["endAt"] is not None
        
        # Verify orders are included
        assert "orders" in daemon_data
        assert len(daemon_data["orders"]) == 3
        
        # Verify order details
        order_ids = [o["id"] for o in daemon_data["orders"]]
        assert "test-order-full-001" in order_ids
        assert "test-order-full-002" in order_ids
        assert "test-order-full-003" in order_ids
        
        # Verify transactions are included in orders
        for order in daemon_data["orders"]:
            assert "evmTransactions" in order
            if order["id"] == "test-order-full-001":
                assert len(order["evmTransactions"]) == 1
                assert order["evmTransactions"][0]["hash"] == tx1.hash
            elif order["id"] == "test-order-full-002":
                assert len(order["evmTransactions"]) == 1
                assert order["evmTransactions"][0]["hash"] == tx2.hash
    
    def test_get_service_daemon_with_config(
        self,
        authorized_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test retrieval of daemon with custom configuration."""
        # Arrange
        # Create daemon with custom config
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-config-001",
            account_id="test-user-id-123",
            org_id="test-org-config",
            service_id="test-service-config",
            status=DaemonStatus.READY_TO_START,
            daemon_config={
                "payment_channel_storage_type": "etcd",
                "service_endpoint": "https://custom-endpoint.ai",
                "service_credentials": [
                    {"key": "API_KEY", "value": "secret-key", "location": "header"}
                ]
            }
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Prepare event
        event = authorized_event.copy()
        event["pathParameters"] = {"daemonId": daemon.id}
        event["httpMethod"] = "GET"
        event["resource"] = "/daemon/{daemonId}"
        
        # Act
        response = get_service_daemon(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        
        body = json.loads(response["body"])
        daemon_data = body["data"]
        
        # Verify daemon config is included
        assert "daemonConfig" in daemon_data
        assert daemon_data["daemonConfig"]["service_endpoint"] == "https://custom-endpoint.ai"
        assert "service_credentials" in daemon_data["daemonConfig"]
        assert len(daemon_data["daemonConfig"]["service_credentials"]) == 1
        
        # Verify empty orders list when no orders exist
        assert "orders" in daemon_data
        assert daemon_data["orders"] == []
    
    def test_get_service_daemon_forbidden_for_other_user(
        self,
        get_service_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test that users cannot access other users' daemons."""
        # Arrange
        # Create daemon with DIFFERENT account_id
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-other-user",
            account_id="different-user-456",  # Different user!
            org_id="test-org",
            service_id="test-service"
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Prepare event to access this daemon
        event = get_service_daemon_event
        event["pathParameters"]["daemonId"] = "test-daemon-other-user"
        
        # Act
        response = get_service_daemon(event, lambda_context)
        
        # Assert - should fail with 403 Forbidden
        assert response["statusCode"] == StatusCode.FORBIDDEN
        
        body = json.loads(response["body"])
        assert body["status"] == "failed"
        assert "error" in body
