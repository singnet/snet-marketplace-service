"""
Integration tests for update_config handler.
"""
import copy
import json

from deployer.application.handlers.daemon_handlers import update_config
from deployer.infrastructure.models import DaemonStatus
from common.constant import StatusCode


class TestUpdateConfigHandler:
    """Test cases for update_config handler."""

    # Bug fixed: Now properly creates a copy of daemon_config to ensure SQLAlchemy change detection
    def test_update_config_success_daemon_down(
        self,
        update_config_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        test_session_factory
    ):
        """Test successful config update for daemon with DOWN status (no redeploy needed)."""
        # Arrange
        initial_config = {
            "payment_channel_storage_type": "etcd",
            "service_endpoint": "https://old-endpoint.example.com",
            "service_credentials": [
                {"key": "OLD_KEY", "value": "old-value", "location": "header"}
            ]
        }
        
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-001",
            account_id="test-user-id-123",  # Must match authorized_event for authorization
            org_id="test-org",
            service_id="test-service",
            status=DaemonStatus.DOWN,  # Daemon is not running
            daemon_config=initial_config,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-001")

        # Create a copy of the event to avoid side effects
        event = copy.deepcopy(update_config_event)
        event["pathParameters"]["daemonId"] = "test-daemon-001"
        event["body"] = json.dumps({
            "serviceEndpoint": "https://updated-endpoint.example.com",
            "serviceCredentials": [
                {
                    "key": "NEW_API_KEY",
                    "value": "new-secret-value",
                    "location": "header"
                }
            ]
        })

        # Act
        response = update_config(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}
        
        # Verify config was updated in the database
        # Need to create new session to see changes from handler's session
        db_session.rollback()
        db_session.close()
        
        new_session = test_session_factory()
        try:
            updated_daemon = daemon_repo.get_daemon(new_session, "test-daemon-001")
            
            # Test EXPECTED behavior
            assert updated_daemon.daemon_config["service_endpoint"] == "https://updated-endpoint.example.com"
            assert updated_daemon.daemon_config["service_credentials"][0]["key"] == "NEW_API_KEY"
            assert updated_daemon.daemon_config["service_credentials"][0]["value"] == "new-secret-value"
            assert updated_daemon.daemon_config["service_credentials"][0]["location"] == "header"
            # Original config should still be preserved
            assert updated_daemon.daemon_config["payment_channel_storage_type"] == "etcd"
        finally:
            new_session.close()

    def test_update_config_success_daemon_up_triggers_redeploy(
        self,
        update_config_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        test_session_factory
    ):
        """Test successful config update for daemon with UP status (triggers redeploy)."""
        # Arrange
        initial_config = {
            "payment_channel_storage_type": "etcd",
            "service_endpoint": "https://current-endpoint.example.com"
        }
        
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-002",
            account_id="test-user-id-123",  # Must match authorized_event
            org_id="test-org-2",
            service_id="test-service-2",
            status=DaemonStatus.UP,  # Daemon is running
            daemon_config=initial_config,
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-002")

        # Create event with only endpoint update (no credentials)
        event = copy.deepcopy(update_config_event)
        event["pathParameters"]["daemonId"] = "test-daemon-002"
        event["body"] = json.dumps({
            "serviceEndpoint": "https://production-endpoint.example.com"
        })

        # Act
        # Note: DeployerClient.redeploy_daemon is handled by global mock_boto3_client fixture
        response = update_config(event, lambda_context)

        # Assert
        assert response["statusCode"] == StatusCode.OK
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["data"] == {}
        
        # Verify config was updated
        # Close current session and create new one to see changes
        db_session.rollback()
        db_session.close()
        
        new_session = test_session_factory()
        try:
            updated_daemon = daemon_repo.get_daemon(new_session, "test-daemon-002")
            assert updated_daemon.daemon_config["service_endpoint"] == "https://production-endpoint.example.com"
            # Original config should still be preserved
            assert updated_daemon.daemon_config["payment_channel_storage_type"] == "etcd"
            # Status should remain UP
            assert updated_daemon.status == DaemonStatus.UP
        finally:
            new_session.close()

    def test_update_config_blocked_when_daemon_starting(
        self,
        update_config_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
        test_session_factory
    ):
        """Test that config update is blocked when daemon is in STARTING status."""
        # Arrange
        daemon = test_data_factory.create_daemon(
            daemon_id="test-daemon-003",
            account_id="test-user-id-123",
            org_id="test-org-3",
            service_id="test-service-3",
            status=DaemonStatus.STARTING,  # Daemon is being deployed
            service_published=True
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()
        
        # Publish daemon
        test_data_factory.publish_daemon(db_session, "test-daemon-003")

        event = copy.deepcopy(update_config_event)
        event["pathParameters"]["daemonId"] = "test-daemon-003"

        # Act
        response = update_config(event, lambda_context)

        # Assert - Should return 400 Bad Request
        assert response["statusCode"] == StatusCode.BAD_REQUEST
        body = json.loads(response["body"])
        assert body["status"] == "failed"
        assert "unavailable during deploying" in body["error"]["message"]
        
        # Verify config was NOT updated
        db_session.rollback()
        db_session.close()
        
        new_session = test_session_factory()
        try:
            unchanged_daemon = daemon_repo.get_daemon(new_session, "test-daemon-003")
            assert unchanged_daemon.daemon_config.get("service_endpoint") != "https://new-endpoint.example.com"
        finally:
            new_session.close()
