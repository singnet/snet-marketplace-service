"""
Integration tests for start_daemon_for_claiming handler.
"""
import copy
import json
from datetime import datetime, UTC, timedelta
from unittest.mock import patch

from deployer.application.handlers.daemon_handlers import start_daemon_for_claiming
from deployer.infrastructure.models import DaemonStatus, ClaimingPeriodStatus
from common.constant import StatusCode


class TestStartDaemonForClaimingHandler:
    """Test cases for start_daemon_for_claiming handler."""

    def test_start_daemon_for_claiming_success_no_previous_claiming(
        self,
        start_daemon_for_claiming_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        claiming_period_repo
    ):
        """Test successful daemon start for claiming when no previous claiming period exists."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-001",
            account_id="test-user-id-123",  # Must match authorized_event
            org_id="test-org",
            service_id="test-service",
            status=DaemonStatus.DOWN,  # Required status for claiming
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Create a copy of the event to avoid side effects
        event = copy.deepcopy(start_daemon_for_claiming_event)
        event["pathParameters"]["daemonId"] = "test-daemon-001"

        # Act
        # Mock datetime.now to return datetime without timezone (matching DB format)
        # This is necessary because DB stores datetime without timezone,
        # but service uses datetime.now(UTC) which has timezone
        def mock_now(tz=None):
            return datetime.now().replace(tzinfo=None)
        
        with patch('deployer.application.services.daemon_service.datetime') as mock_datetime:
            mock_datetime.now = mock_now
            mock_datetime.UTC = UTC
            mock_datetime.timedelta = timedelta
            
            # Note: DeployerClient.start_daemon is handled by global mock_boto3_client fixture
            response = start_daemon_for_claiming(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}
        
        # Verify claiming period was created
        claiming_period = claiming_period_repo.get_last_claiming_period(db_session, "test-daemon-001")
        assert claiming_period is not None
        assert claiming_period.daemon_id == "test-daemon-001"
        assert claiming_period.status == ClaimingPeriodStatus.ACTIVE

    def test_start_daemon_for_claiming_success_with_old_claiming_period(
        self,
        start_daemon_for_claiming_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        claiming_period_repo
    ):
        """Test successful daemon start for claiming when previous claiming period is old enough."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-002",
            account_id="test-user-id-123",  # Must match authorized_event
            org_id="test-org-2",
            service_id="test-service-2",
            status=DaemonStatus.DOWN,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()  # Commit daemon before creating claiming_period (foreign key constraint)
        
        # Create an old claiming period that ended more than BREAK_PERIOD_IN_HOURS ago
        # Since BREAK_PERIOD_IN_HOURS is 0 in config, any past time should work
        # IMPORTANT: Use datetime without timezone since DB stores without timezone
        old_end_time = datetime.now() - timedelta(hours=25)  # 25 hours ago
        old_start_time = old_end_time - timedelta(hours=24)
        
        # Use the repository to create the claiming period properly
        from deployer.infrastructure.models import ClaimingPeriod
        claiming_period_model = ClaimingPeriod(
            daemon_id="test-daemon-002",
            start_at=old_start_time,
            end_at=old_end_time,
            status=ClaimingPeriodStatus.INACTIVE
        )
        db_session.add(claiming_period_model)
        db_session.commit()

        # Create a copy of the event to avoid side effects
        event = copy.deepcopy(start_daemon_for_claiming_event)
        event["pathParameters"]["daemonId"] = "test-daemon-002"

        # Act
        # Mock datetime.now to return datetime without timezone (matching DB format)
        # This fixes the timezone mismatch between DB (no timezone) and service (with timezone)
        def mock_now(tz=None):
            # Always return datetime without timezone to match DB format
            return datetime.now().replace(tzinfo=None)
        
        with patch('deployer.application.services.daemon_service.datetime') as mock_datetime:
            # Make datetime.now() return current time without timezone
            mock_datetime.now = mock_now
            # Keep other datetime functionality working
            mock_datetime.UTC = UTC
            mock_datetime.timedelta = timedelta
            
            # Note: DeployerClient.start_daemon is handled by global mock_boto3_client fixture
            response = start_daemon_for_claiming(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}
        
        # Verify new claiming period was created
        latest_claiming_period = claiming_period_repo.get_last_claiming_period(db_session, "test-daemon-002")
        assert latest_claiming_period is not None
        assert latest_claiming_period.daemon_id == "test-daemon-002"
        assert latest_claiming_period.status == ClaimingPeriodStatus.ACTIVE
        # Verify it's a new claiming period (not the old one)
        assert latest_claiming_period.start_at > old_end_time
