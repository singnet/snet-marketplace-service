"""
Integration tests for redeploy_daemon handler.

This handler is an internal operation: it triggers HaaS to redeploy a daemon.
Preconditions from business logic:
- Daemon must exist, otherwise DaemonNotFoundException -> error response
- Daemon must be in UP state, otherwise handler returns {} and does nothing
- On success, HaaSClient.redeploy_daemon is called and daemon status is set to RESTARTING
"""

import copy
import json
from unittest.mock import patch, MagicMock

from sqlalchemy import text

from deployer.application.handlers.daemon_handlers import redeploy_daemon
from deployer.infrastructure.models import DaemonStatus
from common.constant import StatusCode


class TestRedeployDaemonHandler:
    def test_redeploy_daemon_success_when_up(
        self,
        redeploy_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
    ):
        """Happy path: daemon exists, status=UP -> HaaS is called, status -> RESTARTING."""
        # Arrange: create a daemon in UP state with full config required by HaaS
        daemon_cfg = {
            "payment_channel_storage_type": "etcd",
            "daemon_group": "default-group",
            "service_class": "standard",
            "service_endpoint": "https://svc.example.com",
            # optional: "service_credentials": [...]
        }
        daemon = test_data_factory.create_daemon(
            daemon_id="daemon-up-001",
            account_id="test-user-id-123",
            org_id="org-x",
            service_id="svc-x",
            status=DaemonStatus.UP,
            service_published=True,   # not required by redeploy, but harmless
            daemon_config=daemon_cfg,
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        event = copy.deepcopy(redeploy_daemon_event)
        event["pathParameters"]["daemonId"] = "daemon-up-001"

        # Act: patch the HaaS client where it is used
        with patch("deployer.application.services.daemon_service.HaaSClient") as mock_cls:
            mock = MagicMock()
            mock_cls.return_value = mock
            mock.redeploy_daemon.return_value = {"status": "success"}

            response = redeploy_daemon(event, lambda_context)

            # Assert HTTP contract
            assert response["statusCode"] == StatusCode.OK
            body = json.loads(response["body"])
            assert body["status"] == "success"
            assert body["data"] == {}
            assert "error" in body

            # Assert HaaS call args
            mock.redeploy_daemon.assert_called_once()
            call_kwargs = mock.redeploy_daemon.call_args.kwargs
            assert call_kwargs["org_id"] == "org-x"
            assert call_kwargs["service_id"] == "svc-x"
            assert call_kwargs["daemon_config"] == daemon_cfg

        # Assert status transition to RESTARTING
        updated = daemon_repo.get_daemon(db_session, "daemon-up-001")
        assert updated.status == DaemonStatus.RESTARTING

    def test_redeploy_daemon_returns_empty_when_not_up(
        self,
        redeploy_daemon_event,
        lambda_context,
        db_session,
        test_data_factory,
        daemon_repo,
    ):
        """If daemon is not UP -> do nothing (return {}), do not call HaaS, keep status."""
        daemon = test_data_factory.create_daemon(
            daemon_id="daemon-down-001",
            org_id="org-y",
            service_id="svc-y",
            status=DaemonStatus.DOWN,   # not UP
            daemon_config={"payment_channel_storage_type": "etcd"},
        )
        daemon_repo.create_daemon(db_session, daemon)
        db_session.commit()

        event = copy.deepcopy(redeploy_daemon_event)
        event["pathParameters"]["daemonId"] = "daemon-down-001"

        # Patch HaaS to verify it is NOT called
        with patch("deployer.application.services.daemon_service.HaaSClient") as mock_cls:
            mock = MagicMock()
            mock_cls.return_value = mock

            response = redeploy_daemon(event, lambda_context)

            assert response["statusCode"] == StatusCode.OK
            body = json.loads(response["body"])
            assert body["status"] == "success"
            assert body["data"] == {}

            mock.redeploy_daemon.assert_not_called()

        # Status should be unchanged
        current = daemon_repo.get_daemon(db_session, "daemon-down-001")
        assert current.status == DaemonStatus.DOWN

    def test_redeploy_daemon_not_found_returns_error(
        self,
        redeploy_daemon_event,
        lambda_context,
    ):
        """If daemon does not exist -> exception -> error response from handler."""
        event = copy.deepcopy(redeploy_daemon_event)
        event["pathParameters"]["daemonId"] = "non-existent-id"

        with patch("deployer.application.services.daemon_service.HaaSClient") as mock_cls:
            mock = MagicMock()
            mock_cls.return_value = mock

            response = redeploy_daemon(event, lambda_context)

            # Expect error status code (depends on your exception_handler mapping)
            assert response["statusCode"] >= 400
            body = json.loads(response["body"])
            assert body.get("status") in {"error", "failed", "failure"}

            mock.redeploy_daemon.assert_not_called()
