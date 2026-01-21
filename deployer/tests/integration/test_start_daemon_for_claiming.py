"""
Integration tests for start_daemon_for_claiming handler.
"""
import copy
import json
from datetime import datetime, timedelta, UTC

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
        
        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-001")

        # Create a copy of the event to avoid side effects
        event = copy.deepcopy(start_daemon_for_claiming_event)
        event["pathParameters"]["daemonId"] = "test-daemon-001"

        # Act
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
        
        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-002")
        
        # Create an old claiming period that ended more than 24 hours ago
        # IMPORTANT: Use UTC time to match service logic (datetime.now(UTC))
        # Then remove tzinfo because DB stores naive datetime
        old_end_time = (datetime.now(UTC) - timedelta(hours=25)).replace(tzinfo=None)
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
