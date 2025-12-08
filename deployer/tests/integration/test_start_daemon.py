"""
Integration tests for start_daemon handler.

This handler is an internal handler used to start daemons via HaaS.
It does not require authentication.
"""
import json
import copy

from deployer.application.handlers.daemon_handlers import start_daemon
from deployer.infrastructure.models import DaemonStatus
from common.constant import StatusCode


class TestStartDaemonHandler:
    """Test cases for start_daemon handler."""

    def test_start_daemon_success_ready_to_start(
        self,
        start_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        mock_haas_client
    ):
        """Test successful daemon start when daemon is READY_TO_START and service is published."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-start-001",
            account_id="test-user-id-123",
            org_id="test-org-1",
            service_id="test-service-1",
            status=DaemonStatus.READY_TO_START,
            service_published=True,  # Required for starting
            daemon_config={
                "payment_channel_storage_type": "etcd",
                "service_endpoint": "https://test-service.example.com",
                "provider_wallet_address": "0xProvider1234567890abcdef1234567890abcdef",
            },
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-start-001")
        
        # Update event with correct daemon ID
        event = copy.deepcopy(start_daemon_event)
        event["pathParameters"]["daemonId"] = "test-daemon-start-001"

        # Configure mock response
        mock_haas_client.start_daemon.return_value = {"status": "success"}

        # Act
        response = start_daemon(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}

        # Verify HaaS client was called with correct parameters
        mock_haas_client.start_daemon.assert_called_once_with(
            org_id="test-org-1",
            service_id="test-service-1",
            daemon_config=daemon.daemon_config,
        )

        # Verify daemon status was updated to STARTING
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-start-001")
        assert updated_daemon.status == DaemonStatus.STARTING

    def test_start_daemon_success_not_ready_status(
        self,
        start_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        mock_haas_client
    ):
        """Test start_daemon returns empty when daemon is not in READY_TO_START status."""
        # Arrange - Create daemon with UP status (already running)
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-start-002",
            account_id="test-user-id-123",
            org_id="test-org-2",
            service_id="test-service-2",
            status=DaemonStatus.UP,  # Not READY_TO_START
            service_published=True,
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-start-002")

        # Update event with correct daemon ID
        event = copy.deepcopy(start_daemon_event)
        event["pathParameters"]["daemonId"] = "test-daemon-start-002"

        # Act
        response = start_daemon(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}  # Empty response, no action taken

        # Verify HaaS client was NOT called
        mock_haas_client.start_daemon.assert_not_called()

        # Verify daemon status remained unchanged
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-start-002")
        assert updated_daemon.status == DaemonStatus.UP  # Status unchanged

    def test_start_daemon_success_service_not_published(
        self,
        start_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        mock_haas_client
    ):
        """Test start_daemon returns empty when service is not published."""
        # Arrange - Create daemon with READY_TO_START but service not published
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-start-003",
            account_id="test-user-id-123",
            org_id="test-org-3",
            service_id="test-service-3",
            status=DaemonStatus.READY_TO_START,
            service_published=False,  # Service not published yet
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        # Update event with correct daemon ID
        event = copy.deepcopy(start_daemon_event)
        event["pathParameters"]["daemonId"] = "test-daemon-start-003"

        # Act
        response = start_daemon(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}  # Empty response, no action taken

        # Verify HaaS client was NOT called
        mock_haas_client.start_daemon.assert_not_called()

        # Verify daemon status remained unchanged
        updated_daemon = daemon_repo.get_daemon(db_session, "test-daemon-start-003")
        assert updated_daemon.status == DaemonStatus.READY_TO_START  # Status unchanged
