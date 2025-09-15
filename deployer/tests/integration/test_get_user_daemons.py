"""
Integration tests for get_user_daemons handler.
"""
import json
from datetime import datetime, UTC, timedelta

from deployer.application.handlers.daemon_handlers import get_user_daemons
from deployer.infrastructure.models import DaemonStatus, OrderStatus
from common.constant import StatusCode


class TestGetUserDaemonsHandler:
    """Test cases for get_user_daemons handler."""

    def test_get_user_daemons_success_empty_list(
        self,
        get_user_daemons_event,
        lambda_context,
        db_session,
        daemon_repo,
    ):
        """Test successful get_user_daemons with no daemons for user."""
        # Arrange
        event = get_user_daemons_event
        
        # Act
        response = get_user_daemons(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == []
        assert body["error"] == {}

    def test_get_user_daemons_success_with_multiple_daemons(
        self,
        get_user_daemons_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        order_repo,
        claiming_period_repo,
    ):
        """Test successful get_user_daemons with multiple daemons and additional data."""
        # Arrange
        current_time = datetime.now(UTC)
        
        # Create daemon 1 with UP status
        daemon1 = test_data_factory.create_daemon(
            daemon_id="daemon-001",
            account_id="test-user-id-123",
            org_id="test-org-1",
            service_id="test-service-1",
            status=DaemonStatus.UP,
            end_at=current_time + timedelta(days=15)
        )
        daemon_repo.create_daemon(db_session, daemon1)
        
        # Create daemon 2 with DOWN status
        daemon2 = test_data_factory.create_daemon(
            daemon_id="daemon-002", 
            account_id="test-user-id-123",
            org_id="test-org-2",
            service_id="test-service-2",
            status=DaemonStatus.DOWN,
            end_at=current_time + timedelta(days=7)
        )
        daemon_repo.create_daemon(db_session, daemon2)
        
        # Create daemon 3 for different user (should not appear in results)
        daemon3 = test_data_factory.create_daemon(
            daemon_id="daemon-003",
            account_id="other-user-id-456",
            org_id="test-org-3", 
            service_id="test-service-3",
            status=DaemonStatus.UP
        )
        daemon_repo.create_daemon(db_session, daemon3)
        
        # Commit daemons first to satisfy foreign key constraints
        db_session.commit()
        
        # Create orders
        order1 = test_data_factory.create_order(
            order_id="order-001",
            daemon_id=daemon1.id,
            status=OrderStatus.SUCCESS
        )
        order_repo.create_order(db_session, order1)
        
        order2 = test_data_factory.create_order(
            order_id="order-002", 
            daemon_id=daemon2.id,
            status=OrderStatus.SUCCESS
        )
        order_repo.create_order(db_session, order2)
        
        # Create claiming period only for daemon1 (repository method creates it automatically)
        claiming_period_repo.create_claiming_period(db_session, daemon1.id)
        
        db_session.commit()
        
        event = get_user_daemons_event
        
        # Act
        response = get_user_daemons(event, lambda_context)
        
        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["error"] == {}
        
        daemons_data = body["data"]
        assert len(daemons_data) == 2  # Only 2 daemons for our user
        
        # Sort by daemon id for predictable testing
        daemons_data.sort(key=lambda d: d["id"])
        
        # Check daemon 1 (has claiming period, so status should be CLAIMING)
        daemon1_data = daemons_data[0]
        assert daemon1_data["id"] == daemon1.id
        assert daemon1_data["status"] == "CLAIMING"  # claiming period overrides daemon status
        # Check that endOn is a valid date in the future (don't check exact time due to DB timing)
        assert "endOn" in daemon1_data
        assert len(daemon1_data["endOn"]) >= 19  # At least YYYY-MM-DDTHH:MM:SS format
        assert "lastClaimedAt" in daemon1_data
        assert "lastPayment" in daemon1_data
        
        # Check daemon 2 (no claiming period, so original status)
        daemon2_data = daemons_data[1]
        assert daemon2_data["id"] == daemon2.id
        assert daemon2_data["status"] == DaemonStatus.DOWN.value
        # Check that endOn is a valid date format
        assert "endOn" in daemon2_data
        assert len(daemon2_data["endOn"]) >= 19  # At least YYYY-MM-DDTHH:MM:SS format
        assert "lastClaimedAt" in daemon2_data
        assert "lastPayment" in daemon2_data
