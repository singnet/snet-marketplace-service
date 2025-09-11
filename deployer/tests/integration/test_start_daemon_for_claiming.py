"""
Integration tests for start_daemon_for_claiming handler.
"""
import json
import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import patch, MagicMock

from deployer.application.handlers.daemon_handlers import start_daemon_for_claiming
from deployer.infrastructure.models import DaemonStatus, ClaimingPeriodStatus
from deployer.config import CLAIMING_PERIOD_IN_HOURS, BREAK_PERIOD_IN_HOURS
from common.constant import StatusCode


class TestStartDaemonForClaimingHandler:
    """Test cases for start_daemon_for_claiming handler."""
    
    def test_start_daemon_for_claiming_first_time(
        self,
        authorized_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        claiming_period_repo
    ):
        """Test successful daemon start for claiming when no previous claiming exists."""
        # Arrange
        # Create daemon with DOWN status (required for claiming)
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-claim-001",
            account_id="test-user-id-123",
            org_id="test-org-claim",
            service_id="test-service-claim",
            status=DaemonStatus.DOWN
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Prepare event
        event = authorized_event.copy()
        event["pathParameters"] = {"daemonId": daemon.id}
        event["httpMethod"] = "GET"
        event["resource"] = "/daemon/{daemonId}/start"
        event["path"] = f"/daemon/{daemon.id}/start"
        
        # Mock DeployerClient to avoid actual daemon start
        with patch('deployer.application.services.daemon_service.DeployerClient') as mock_deployer:
            mock_client = MagicMock()
            mock_deployer.return_value = mock_client
            mock_client.start_daemon.return_value = {"status": "success"}
            
            # Act
            response = start_daemon_for_claiming(event, lambda_context)
            
            # Assert
            assert response["statusCode"] == StatusCode.OK
            
            body = json.loads(response["body"])
            assert body["status"] == "success"
            assert body["data"] == {}  # Method returns empty dict on success
            
            # Verify claiming period was created
            last_claiming = claiming_period_repo.get_last_claiming_period(
                db_session, 
                daemon.id
            )
            assert last_claiming is not None
            assert last_claiming.daemon_id == daemon.id
            assert last_claiming.status == ClaimingPeriodStatus.ACTIVE
            
            # Verify DeployerClient was called
            mock_client.start_daemon.assert_called_once_with(daemon.id)
    
    def test_start_daemon_for_claiming_after_break_period(
        self,
        authorized_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        claiming_period_repo
    ):
        """Test successful daemon start for claiming after break period has passed."""
        # Arrange
        # Create daemon with DOWN status
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-claim-002",
            account_id="test-user-id-123",
            org_id="test-org-claim-2",
            service_id="test-service-claim-2",
            status=DaemonStatus.DOWN
        )
        daemon_repo.create_daemon(db_session, daemon)
        
        # Create old claiming period that ended long ago (beyond break period)
        old_claiming_time = datetime.now(UTC) - timedelta(hours=BREAK_PERIOD_IN_HOURS + 1)
        old_claiming = test_data_factory.create_claiming_period(
            daemon_id=daemon.id,
            status=ClaimingPeriodStatus.INACTIVE,
            start_at=old_claiming_time - timedelta(hours=CLAIMING_PERIOD_IN_HOURS),
            end_at=old_claiming_time
        )
        
        # Save old claiming period manually
        from deployer.infrastructure.models import ClaimingPeriod
        old_claiming_model = ClaimingPeriod(
            daemon_id=old_claiming.daemon_id,
            start_at=old_claiming.start_at,
            end_at=old_claiming.end_at,
            status=old_claiming.status
        )
        db_session.add(old_claiming_model)
        db_session.commit()
        
        # Prepare event
        event = authorized_event.copy()
        event["pathParameters"] = {"daemonId": daemon.id}
        event["httpMethod"] = "GET"
        event["resource"] = "/daemon/{daemonId}/start"
        event["path"] = f"/daemon/{daemon.id}/start"
        
        # Mock DeployerClient
        with patch('deployer.application.services.daemon_service.DeployerClient') as mock_deployer:
            mock_client = MagicMock()
            mock_deployer.return_value = mock_client
            mock_client.start_daemon.return_value = {"status": "success"}
            
            # Act
            response = start_daemon_for_claiming(event, lambda_context)
            
            # Assert
            assert response["statusCode"] == StatusCode.OK
            
            body = json.loads(response["body"])
            assert body["status"] == "success"
            assert body["data"] == {}
            
            # Verify new claiming period was created
            claiming_periods = db_session.query(ClaimingPeriod).filter_by(
                daemon_id=daemon.id
            ).order_by(ClaimingPeriod.end_at.desc()).all()
            
            assert len(claiming_periods) == 2  # Old one and new one
            
            newest_claiming = claiming_periods[0]
            assert newest_claiming.status == ClaimingPeriodStatus.ACTIVE
            assert newest_claiming.end_at > old_claiming.end_at  # New claiming is more recent
            
            # Verify DeployerClient was called
            mock_client.start_daemon.assert_called_once_with(daemon.id)
