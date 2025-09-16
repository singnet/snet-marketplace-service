"""
Integration tests for stop_daemon handler.

This handler is an internal handler used to stop daemons via HaaS.
It does not require authentication.
"""
import json
import copy
from unittest.mock import patch, MagicMock

from deployer.application.handlers.daemon_handlers import stop_daemon
from deployer.infrastructure.models import DaemonStatus
from common.constant import StatusCode


class TestStopDaemonHandler:
    """Test cases for stop_daemon handler."""

    def test_stop_daemon_success_daemon_up(
        self,
        stop_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
    ):
        """Test successful daemon stop when daemon is UP."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-stop-001",
            account_id="test-user-id-123",
            org_id="test-org-1",
            service_id="test-service-1",
            status=DaemonStatus.UP,  # Required status for stopping
            service_published=True,
            daemon_config={
                "payment_channel_storage_type": "etcd",
                "service_endpoint": "https://test-service.example.com",
                "provider_wallet_address": "0xProvider1234567890abcdef1234567890abcdef",
            },
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Update event with correct daemon ID
        event = copy.deepcopy(stop_daemon_event)
        event["pathParameters"]["daemonId"] = "test-daemon-stop-001"

        # Act - Mock HaaSClient at the class level before handler execution
        with patch("deployer.application.services.daemon_service.HaaSClient") as mock_haas_class:
            mock_haas_instance = MagicMock()
            mock_haas_class.return_value = mock_haas_instance
            mock_haas_instance.delete_daemon.return_value = {"status": "success"}

            response = stop_daemon(event, lambda_context)

            # Assert
            assert response["statusCode"] == StatusCode.OK
            body = json.loads(response["body"])
            assert body["status"] == "success"
            assert body["data"] == {}

            # Verify HaaS client was called with correct parameters
            mock_haas_instance.delete_daemon.assert_called_once_with(
                "test-org-1",
                "test-service-1",
            )

        # Verify daemon status was updated to DELETING
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-stop-001")
        assert updated_daemon.status == DaemonStatus.DELETING

    def test_stop_daemon_success_not_up_status(
        self,
        stop_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
    ):
        """Test stop_daemon returns empty when daemon is not in UP status."""
        # Arrange - Create daemon with DOWN status (already stopped)
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-stop-002",
            account_id="test-user-id-123",
            org_id="test-org-2",
            service_id="test-service-2",
            status=DaemonStatus.DOWN,  # Not UP
            service_published=True,
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Update event with correct daemon ID
        event = copy.deepcopy(stop_daemon_event)
        event["pathParameters"]["daemonId"] = "test-daemon-stop-002"

        # Act
        with patch("deployer.application.services.daemon_service.HaaSClient") as mock_haas_class:
            mock_haas_instance = MagicMock()
            mock_haas_class.return_value = mock_haas_instance

            response = stop_daemon(event, lambda_context)

            # Assert
            assert response["statusCode"] == StatusCode.OK
            body = json.loads(response["body"])
            assert body["status"] == "success"
            assert body["data"] == {}  # Empty response, no action taken

            # Verify HaaS client was NOT called
            mock_haas_instance.delete_daemon.assert_not_called()

        # Verify daemon status remained unchanged
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-stop-002")
        assert updated_daemon.status == DaemonStatus.DOWN  # Status unchanged

    def test_stop_daemon_success_multiple_status_scenarios(
        self,
        stop_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
    ):
        """Test stop_daemon with various daemon statuses (only UP should trigger stop)."""
        # Arrange - Create daemons with different statuses
        statuses_to_test = [
            (DaemonStatus.INIT, False),
            (DaemonStatus.READY_TO_START, False),
            (DaemonStatus.STARTING, False),
            (DaemonStatus.UP, True),  # Only this should trigger stop
            (DaemonStatus.RESTARTING, False),
            (DaemonStatus.DELETING, False),
            (DaemonStatus.DOWN, False),
        ]

        for idx, (status, should_stop) in enumerate(statuses_to_test):
            daemon_id = f"test-daemon-stop-multi-{idx:03d}"
            daemon = test_data_factory.create_daemon(
                daemon_id=daemon_id,
                account_id="test-user-id-123",
                org_id=f"test-org-{idx}",
                service_id=f"test-service-{idx}",
                status=status,
                service_published=True,
            )
            daemon_repo.create_daemon(db_session, daemon)
            db_session.commit()

            # Update event with correct daemon ID
            event = copy.deepcopy(stop_daemon_event)
            event["pathParameters"]["daemonId"] = daemon_id

            # Act - Mock HaaSClient for each iteration
            with patch("deployer.application.services.daemon_service.HaaSClient") as mock_haas_class:
                mock_haas_instance = MagicMock()
                mock_haas_class.return_value = mock_haas_instance
                mock_haas_instance.delete_daemon.return_value = {"status": "success"}

                response = stop_daemon(event, lambda_context)

                # Assert
                assert response["statusCode"] == StatusCode.OK
                body = json.loads(response["body"])
                assert body["status"] == "success"
                assert body["data"] == {}

                # Verify HaaS client was called only for UP status
                if should_stop:
                    mock_haas_instance.delete_daemon.assert_called_once_with(
                        f"test-org-{idx}",
                        f"test-service-{idx}",
                    )
                    # Verify status change to DELETING
                    updated_daemon = daemon_repo.get_daemon(db_session, daemon_id)
                    assert updated_daemon.status == DaemonStatus.DELETING
                else:
                    mock_haas_instance.delete_daemon.assert_not_called()
                    # Verify status remained unchanged
                    updated_daemon = daemon_repo.get_daemon(db_session, daemon_id)
                    assert updated_daemon.status == status
