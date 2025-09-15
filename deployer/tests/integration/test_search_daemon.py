"""
Integration tests for search_daemon handler.
"""
import copy
import json

from deployer.application.handlers.daemon_handlers import search_daemon
from deployer.infrastructure.models import DaemonStatus, OrderStatus
from common.constant import StatusCode

# Import TestSessionFactory from conftest


class TestSearchDaemonHandler:
    """Test cases for search_daemon handler."""

    def test_search_daemon_success_with_order(
        self,
        search_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo
    ):
        """Test successful daemon search with existing order."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-001",
            account_id="user-123",  # Note: search_daemon doesn't check authorization
            org_id="snet-org",
            service_id="example-service",
            status=DaemonStatus.UP,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create an order for this daemon
        order = test_data_factory.create_order(
            order_id="test-order-001",
            daemon_id="test-daemon-001",
            status=OrderStatus.SUCCESS
        )
        order_repo.create_order(db_session, order)
        db_session.commit()

        # Create event with search parameters
        event = copy.deepcopy(search_daemon_event)
        event["queryStringParameters"]["orgId"] = "snet-org"
        event["queryStringParameters"]["serviceId"] = "example-service"

        # Act
        response = search_daemon(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        data = body["data"]
        assert "daemon" in data
        assert "order" in data
        
        # Check daemon data
        daemon_data = data["daemon"]
        assert daemon_data["id"] == "test-daemon-001"  # Not daemonId!
        assert daemon_data["orgId"] == "snet-org"
        assert daemon_data["serviceId"] == "example-service"
        assert daemon_data["status"] == "UP"
        # daemonConfig should be removed from response
        assert "daemonConfig" not in daemon_data
        
        # Check order data  
        order_data = data["order"]
        assert order_data["id"] == "test-order-001"  # Not orderId!
        assert order_data["status"] == "SUCCESS"

    def test_search_daemon_not_found(
        self,
        search_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test search for non-existent daemon returns empty result."""
        # Arrange
        # Create some daemons that don't match search criteria
        daemon1 = test_data_factory.create_daemon(
            daemon_id="test-daemon-003",
            org_id="wrong-org",
            service_id="test-service",
            status=DaemonStatus.UP
        )
        daemon2 = test_data_factory.create_daemon(
            daemon_id="test-daemon-004",
            org_id="test-org",
            service_id="wrong-service",
            status=DaemonStatus.UP
        )
        daemon_repo.create_daemon(db_session, daemon1)
        daemon_repo.create_daemon(db_session, daemon2)
        db_session.commit()

        # Create event searching for non-existent combination
        event = copy.deepcopy(search_daemon_event)
        event["queryStringParameters"]["orgId"] = "non-existent-org"
        event["queryStringParameters"]["serviceId"] = "non-existent-service"

        # Act
        response = search_daemon(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # When daemon not found, returns empty dict
        assert body["data"] == {}

    # Bug fixed: Now sorts by updated_at instead of UUID for proper chronological order
    def test_search_daemon_with_multiple_orders(
        self,
        search_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo
    ):
        """Test search daemon returns only the last order when multiple orders exist."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-005",
            account_id="user-456",
            org_id="multi-org",
            service_id="multi-service",
            status=DaemonStatus.UP,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create multiple orders for this daemon
        older_order = test_data_factory.create_order(
            order_id="old-order-001",
            daemon_id="test-daemon-005",
            status=OrderStatus.SUCCESS
        )
        order_repo.create_order(db_session, older_order)
        
        # Commit to ensure older_order gets earlier timestamp
        db_session.commit()
        
        # Create newer order
        newer_order = test_data_factory.create_order(
            order_id="new-order-002",
            daemon_id="test-daemon-005",
            status=OrderStatus.PROCESSING
        )
        order_repo.create_order(db_session, newer_order)
        db_session.commit()

        # Create event with search parameters
        event = copy.deepcopy(search_daemon_event)
        event["queryStringParameters"]["orgId"] = "multi-org"
        event["queryStringParameters"]["serviceId"] = "multi-service"

        # Act
        response = search_daemon(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        data = body["data"]
        # Should return the most recent order
        order_data = data["order"]
        assert order_data["id"] == "new-order-002"  # Not orderId!
        assert order_data["status"] == "PROCESSING"
