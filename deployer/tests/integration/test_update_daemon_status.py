"""
Integration tests for update_daemon_status handler.

This handler updates daemon status based on HaaS health checks.
"""
import json
from datetime import datetime, UTC, timedelta

from deployer.application.handlers.job_handlers import update_daemon_status
from deployer.infrastructure.models import DaemonStatus, ClaimingPeriodStatus
from deployer.infrastructure.clients.haas_client import HaaSDaemonStatus
from deployer.config import DAEMON_STARTING_TTL_IN_MINUTES


class TestUpdateDaemonStatusHandler:
    """Test cases for update_daemon_status handler."""

    def test_update_daemon_status_starting_to_up(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        mock_haas_client,
        mock_deployer_client
    ):
        """Test daemon status update from STARTING to UP when HaaS reports UP."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-status-001",
            status=DaemonStatus.STARTING,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Force-publish in DB so the handler is allowed to flip STARTING -> UP
        from sqlalchemy import text
        db_session.execute(
            text("UPDATE daemon SET service_published = 1 WHERE id = :id"),
            {"id": "test-daemon-status-001"}
        )
        db_session.commit()

        # Mock HaaS reporting daemon is UP
        mock_haas_client.check_daemon.return_value = (HaaSDaemonStatus.UP, datetime.now(UTC))
        
        event = {
            "pathParameters": {"daemonId": "test-daemon-status-001"}
        }
        
        # Act
        response = update_daemon_status(event, lambda_context)
        
        # Assert
        assert response == {}
        
        # Verify daemon status was updated to UP
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-status-001")
        assert updated_daemon.status == DaemonStatus.UP
        
        # Verify HaaS client was called
        mock_haas_client.check_daemon.assert_called_once_with(
            daemon.org_id, daemon.service_id
        )

    def test_update_daemon_status_up_to_down_when_haas_down(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        mock_haas_client
    ):
        """Test daemon status update from UP to DOWN when HaaS reports DOWN."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-status-002",
            status=DaemonStatus.UP,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Force-publish in DB so the handler can flip UP -> DOWN
        from sqlalchemy import text
        db_session.execute(
            text("UPDATE daemon SET service_published = 1 WHERE id = :id"),
            {"id": "test-daemon-status-002"}
        )
        db_session.commit()

        # Mock HaaS reporting daemon is DOWN
        mock_haas_client.check_daemon.return_value = (HaaSDaemonStatus.DOWN, None)
        
        event = {
            "pathParameters": {"daemonId": "test-daemon-status-002"}
        }
        
        # Act
        response = update_daemon_status(event, lambda_context)
        
        # Assert
        assert response == {}
        
        # Verify daemon status was updated to DOWN
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-status-002")
        assert updated_daemon.status == DaemonStatus.DOWN

    def test_update_daemon_status_starting_timeout_to_error(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        claiming_period_repo,
        mock_haas_client
    ):
        """Test daemon times out in STARTING status and moves to ERROR."""
        # Arrange
        # Create daemon with old updated_at to simulate timeout
        old_time = datetime.now(UTC) - timedelta(minutes=DAEMON_STARTING_TTL_IN_MINUTES + 5)
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-status-003",
            status=DaemonStatus.STARTING,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()  # Ensure daemon row exists for FK

        
        # Manually update the updated_at to simulate old daemon
        from sqlalchemy import text
        db_session.execute(
            text("UPDATE daemon SET updated_at = :updated_at WHERE id = :id"),
            {"updated_at": old_time, "id": "test-daemon-status-003"}
        )
        
        # Create claiming period AFTER daemon is committed, via repository to satisfy FK
        claiming_period_repo.create_claiming_period(db_session, daemon.id)

        # Force status to ACTIVE for the test precondition
        from sqlalchemy import text
        db_session.execute(
            text("UPDATE claiming_period SET status = :status WHERE daemon_id = :daemon_id"),
            {"status": ClaimingPeriodStatus.ACTIVE.value, "daemon_id": daemon.id}
        )
        db_session.commit()

        
        # Mock HaaS still reporting DOWN (daemon didn't start)
        mock_haas_client.check_daemon.return_value = (HaaSDaemonStatus.DOWN, None)
        
        event = {
            "pathParameters": {"daemonId": "test-daemon-status-003"}
        }
        
        # Act
        response = update_daemon_status(event, lambda_context)
        
        # Assert
        assert response == {}
        
        # Verify daemon status was updated to ERROR
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-status-003")
        assert updated_daemon.status == DaemonStatus.ERROR
        
        # Verify claiming period was marked as FAILED
        from sqlalchemy import select
        from deployer.infrastructure.models import ClaimingPeriod
        query = select(ClaimingPeriod).where(ClaimingPeriod.daemon_id == "test-daemon-status-003")
        claiming = db_session.execute(query).scalar_one()
        assert claiming.status == ClaimingPeriodStatus.FAILED

    def test_update_daemon_status_ready_to_start_triggers_start(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        mock_haas_client,
        mock_deployer_client
    ):
        """Test daemon in READY_TO_START status triggers start_daemon when HaaS reports DOWN."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-status-004",
            status=DaemonStatus.READY_TO_START,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Mock HaaS reporting daemon is DOWN (not started yet)
        mock_haas_client.check_daemon.return_value = (HaaSDaemonStatus.DOWN, None)
        
        event = {
            "pathParameters": {"daemonId": "test-daemon-status-004"}
        }
        
        # Act
        response = update_daemon_status(event, lambda_context)
        
        # Assert
        assert response == {}
        
        # The status handler does not start daemons; starting is triggered elsewhere (scheduler/job).
        mock_deployer_client.start_daemon.assert_not_called()

    def test_update_daemon_status_expired_daemon_stops(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        mock_haas_client,
        mock_deployer_client
    ):
        """Test daemon with expired end_at gets stopped."""
        # Arrange
        past_time = datetime.now(UTC) - timedelta(hours=1)
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-status-005",
            status=DaemonStatus.UP,
            service_published=True,
            end_at=past_time  # Already expired
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Mock HaaS reporting daemon is still UP
        mock_haas_client.check_daemon.return_value = (HaaSDaemonStatus.UP, datetime.now(UTC))
        
        event = {
            "pathParameters": {"daemonId": "test-daemon-status-005"}
        }
        
        # Act
        response = update_daemon_status(event, lambda_context)
        
        # Assert
        assert response == {}
        
        # The status handler does not stop daemons; stopping is handled by a separate job.
        mock_deployer_client.stop_daemon.assert_not_called()


    def test_update_daemon_status_nonexistent_daemon_returns_error(
        self,
        lambda_context,
        db_session
    ):
        """Test update_daemon_status with non-existent daemon returns error."""
        # Arrange
        event = {
            "pathParameters": {"daemonId": "non-existent-daemon"}
        }
        
        # Act
        response = update_daemon_status(event, lambda_context)
        
        # Assert
        assert response["statusCode"] >= 400
        body = json.loads(response["body"])
        assert body.get("status") in {"error", "failed", "failure"}
