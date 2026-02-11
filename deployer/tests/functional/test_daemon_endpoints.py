from datetime import datetime

from common.logger import get_logger
from deployer.application.handlers.daemon_handlers import (
    get_daemon,
    get_daemon_logs,
    update_config,
    update_daemon_status,
)
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import DaemonStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.tests.functional.utils import (
    generate_request_event,
    validate_response_ok,
    create_common_queue_event,
)

logger = get_logger(__name__)


class TestDaemonEndpoints:
    def test_get_daemon_ok(
        self,
        test_daemon_service,
        test_auth_service,
        add_test_daemon_and_service,
        test_org_id,
        test_service_id,
        test_daemon_id,
    ):
        event = generate_request_event(path_parameters={"daemonId": test_daemon_id})

        response = get_daemon(event, None, test_daemon_service, test_auth_service)
        _, data = validate_response_ok(response)

        assert data["orgId"] == test_org_id
        assert data["serviceId"] == test_service_id
        assert data["id"] == test_daemon_id
        assert data["status"] == DaemonStatus.UP.value
        assert data["daemonConfig"] == {}
        assert data["daemonEndpoint"] == ""

    def test_get_daemon_logs_ok(
        self, test_daemon_service, test_auth_service, add_test_daemon_and_service, test_daemon_id
    ):
        event = generate_request_event(path_parameters={"daemonId": test_daemon_id})

        response = get_daemon_logs(event, None, test_daemon_service, test_auth_service)
        _, data = validate_response_ok(response)

        assert data == ["log1", "log2", "log3"]

    def test_update_config_ok(
        self,
        test_daemon_service,
        test_auth_service,
        test_session_factory,
        add_test_daemon,
        test_org_id,
        test_service_id,
        test_daemon_id,
    ):
        test_endpoint = "http://localhost:8080"
        test_credentials = [
            {"key": "Authorization", "value": "Bearer 1234567890", "location": "headers"}
        ]

        event = generate_request_event(
            path_parameters={"daemonId": test_daemon_id},
            body={"serviceEndpoint": test_endpoint, "serviceCredentials": test_credentials},
        )

        response = update_config(event, None, test_daemon_service, test_auth_service)
        _, _ = validate_response_ok(response)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.daemon_config["service_endpoint"] == test_endpoint
        assert daemon.daemon_config["service_credentials"] == test_credentials

    def test_update_daemon_status_ok(
        self,
        test_daemon_service,
        test_session_factory,
        add_test_daemon,
        test_daemon_id,
        test_org_id,
        test_service_id,
    ):
        # update status the first time
        test_status = "DOWN"
        test_observed_at = "2025-01-15T10:30:00.123456789Z"
        test_resource_version = "123"

        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "status": test_status,
                "observedAt": test_observed_at,
                "resourceVersion": test_resource_version,
            }
        )
        queue_event = create_common_queue_event([event])
        update_daemon_status(queue_event, None, test_daemon_service)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.status.value == test_status
        assert daemon.status_observed_at == datetime.fromisoformat(test_observed_at).replace(
            microsecond=0, tzinfo=None
        )
        assert daemon.status_resource_version == test_resource_version

        # update status with not null status_observed_at and status_resource_version fields
        test_status = "STARTING"
        test_observed_at = "2026-01-15T10:30:00.123456789Z"
        test_resource_version = "234"

        event = generate_request_event(
            body={
                "orgId": test_org_id,
                "serviceId": test_service_id,
                "status": test_status,
                "observedAt": test_observed_at,
                "resourceVersion": test_resource_version,
            }
        )
        queue_event = create_common_queue_event([event])
        update_daemon_status(queue_event, None, test_daemon_service)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.status.value == test_status
        assert daemon.status_observed_at == datetime.fromisoformat(test_observed_at).replace(
            microsecond=0, tzinfo=None
        )
        assert daemon.status_resource_version == test_resource_version

    # def test_deploy_daemon_ok(self, test_daemon_service):
    #     pass
    #
    # def test_redeploy_all_daemons(self, test_daemon_service):
    #     pass
