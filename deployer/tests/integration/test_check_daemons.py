"""
Integration tests for check_daemons handler.

This handler checks the status of all active daemons and triggers status updates.
"""
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC, timedelta

from deployer.application.handlers.job_handlers import check_daemons
from deployer.infrastructure.models import DaemonStatus
from common.constant import StatusCode


class TestCheckDaemonsHandler:
    """Test cases for check_daemons handler."""

    def test_check_daemons_triggers_status_updates(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test that check_daemons triggers status updates for active daemons."""
        # Arrange
        # Create daemons with different statuses
        daemon_up = test_data_factory.create_daemon(
            daemon_id="daemon-check-001",
            status=DaemonStatus.UP,
            service_published=True
        )
        daemon_starting = test_data_factory.create_daemon(
            daemon_id="daemon-check-002",
            status=DaemonStatus.STARTING,
            service_published=True
        )
        daemon_ready = test_data_factory.create_daemon(
            daemon_id="daemon-check-003",
            status=DaemonStatus.READY_TO_START,
            service_published=True  # Will be checked
        )
        daemon_ready_unpublished = test_data_factory.create_daemon(
            daemon_id="daemon-check-004",
            status=DaemonStatus.READY_TO_START,
            service_published=False  # Will be skipped
        )
        # Daemons that should be skipped
        daemon_init = test_data_factory.create_daemon(
            daemon_id="daemon-check-005",
            status=DaemonStatus.INIT
        )
        daemon_error = test_data_factory.create_daemon(
            daemon_id="daemon-check-006",
            status=DaemonStatus.ERROR
        )
        daemon_down = test_data_factory.create_daemon(
            daemon_id="daemon-check-007",
            status=DaemonStatus.DOWN
        )
        
        # Save all daemons
        for daemon in [daemon_up, daemon_starting, daemon_ready, daemon_ready_unpublished, 
                      daemon_init, daemon_error, daemon_down]:
            daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Mock DeployerClient to verify update_daemon_status calls
        with patch("deployer.application.services.job_services.DeployerClient") as mock_deployer_class:
            mock_deployer_instance = MagicMock()
            mock_deployer_class.return_value = mock_deployer_instance
            
            # Act
            response = check_daemons({}, lambda_context)
            
            # Assert
            assert response == {}  # Handler returns empty dict on success
            
            # Verify update_daemon_status was called for active daemons
            # Should be called for: UP, STARTING, and READY_TO_START(published)
            assert mock_deployer_instance.update_daemon_status.call_count == 3
            
            # Get all daemon IDs that were updated
            updated_daemon_ids = [
                call.args[0] for call in mock_deployer_instance.update_daemon_status.call_args_list
            ]
            
            # Verify correct daemons were updated
            assert "daemon-check-001" in updated_daemon_ids  # UP
            assert "daemon-check-002" in updated_daemon_ids  # STARTING
            assert "daemon-check-003" in updated_daemon_ids  # READY_TO_START with published service
            
            # Verify skipped daemons were NOT updated
            assert "daemon-check-004" not in updated_daemon_ids  # READY_TO_START but unpublished
            assert "daemon-check-005" not in updated_daemon_ids  # INIT
            assert "daemon-check-006" not in updated_daemon_ids  # ERROR
            assert "daemon-check-007" not in updated_daemon_ids  # DOWN
            
            # Verify all calls were asynchronous
            for call in mock_deployer_instance.update_daemon_status.call_args_list:
                assert call.kwargs.get("asynchronous") is True

    def test_check_daemons_handles_restarting_and_deleting_statuses(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test that check_daemons also processes RESTARTING and DELETING statuses."""
        # Arrange
        daemon_restarting = test_data_factory.create_daemon(
            daemon_id="daemon-restart-001",
            status=DaemonStatus.RESTARTING,
            service_published=True
        )
        daemon_deleting = test_data_factory.create_daemon(
            daemon_id="daemon-delete-001",
            status=DaemonStatus.DELETING,
            service_published=True
        )
        
        daemon_repo.create_daemon(db_session, daemon_restarting)
        daemon_repo.create_daemon(db_session, daemon_deleting)
        db_session.commit()
        
        # Mock DeployerClient
        with patch("deployer.application.services.job_services.DeployerClient") as mock_deployer_class:
            mock_deployer_instance = MagicMock()
            mock_deployer_class.return_value = mock_deployer_instance
            
            # Act
            response = check_daemons({}, lambda_context)
            
            # Assert
            assert response == {}
            
            # Verify both daemons were checked
            assert mock_deployer_instance.update_daemon_status.call_count == 2
            
            updated_daemon_ids = [
                call.args[0] for call in mock_deployer_instance.update_daemon_status.call_args_list
            ]
            
            assert "daemon-restart-001" in updated_daemon_ids
            assert "daemon-delete-001" in updated_daemon_ids

    def test_check_daemons_with_no_active_daemons(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test check_daemons when there are no daemons to check."""
        # Arrange
        # Create only daemons that should be skipped
        daemon_init = test_data_factory.create_daemon(
            daemon_id="daemon-skip-001",
            status=DaemonStatus.INIT
        )
        daemon_error = test_data_factory.create_daemon(
            daemon_id="daemon-skip-002",
            status=DaemonStatus.ERROR
        )
        daemon_down = test_data_factory.create_daemon(
            daemon_id="daemon-skip-003",
            status=DaemonStatus.DOWN
        )
        
        daemon_repo.create_daemon(db_session, daemon_init)
        daemon_repo.create_daemon(db_session, daemon_error)
        daemon_repo.create_daemon(db_session, daemon_down)
        db_session.commit()
        
        # Mock DeployerClient
        with patch("deployer.application.services.job_services.DeployerClient") as mock_deployer_class:
            mock_deployer_instance = MagicMock()
            mock_deployer_class.return_value = mock_deployer_instance
            
            # Act
            response = check_daemons({}, lambda_context)
            
            # Assert
            assert response == {}
            
            # Verify no daemon status updates were triggered
            mock_deployer_instance.update_daemon_status.assert_not_called()

    def test_check_daemons_handles_error_gracefully(
        self,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo
    ):
        """Test that check_daemons handles errors from DeployerClient gracefully."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="daemon-error-001",
            status=DaemonStatus.UP,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Mock DeployerClient to raise an error
        with patch("deployer.application.services.job_services.DeployerClient") as mock_deployer_class:
            mock_deployer_instance = MagicMock()
            mock_deployer_class.return_value = mock_deployer_instance
            mock_deployer_instance.update_daemon_status.side_effect = Exception("Network error")
            
            # Act
            response = check_daemons({}, lambda_context)
            
            # Assert - handler wraps exception into error response
            assert response["statusCode"] == StatusCode.INTERNAL_SERVER_ERROR
            body = json.loads(response["body"])
            assert body.get("status") in ("failed", "error")
            assert "error" in body
