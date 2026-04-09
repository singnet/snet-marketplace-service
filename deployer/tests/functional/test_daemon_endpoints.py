from datetime import datetime

import pytest

from common.logger import get_logger
from deployer.application.handlers.daemon_handlers import (
    get_daemon,
    get_daemon_logs,
    update_config,
    update_daemon_status,
    redeploy_daemon_forcibly,
)
from deployer.exceptions import DaemonNotFoundForServiceException
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import DaemonStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.tests.functional.utils import (
    generate_request_event,
    validate_response_ok,
    create_common_queue_event,
    validate_response_forbidden,
    validate_response_bad_request,
    add_daemon,
    validate_response_not_found,
)

logger = get_logger(__name__)


class TestGetDaemon:
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

    def test_get_daemon_no_daemon(
        self,
        test_daemon_service,
        test_auth_service,
        test_org_id,
        test_service_id,
        test_daemon_id,
    ):
        event = generate_request_event(path_parameters={"daemonId": test_daemon_id})

        response = get_daemon(event, None, test_daemon_service, test_auth_service)
        _, message = validate_response_forbidden(response)

        assert message == "Access denied"


class TestGetDaemonLogs:
    def test_get_daemon_logs_ok(
        self, test_daemon_service, test_auth_service, add_test_daemon_and_service, test_daemon_id
    ):
        event = generate_request_event(path_parameters={"daemonId": test_daemon_id})

        response = get_daemon_logs(event, None, test_daemon_service, test_auth_service)
        _, data = validate_response_ok(response)

        assert data == ["log1", "log2", "log3"]

    def test_get_daemon_logs_no_daemon(
        self, test_daemon_service, test_auth_service, test_daemon_id
    ):
        event = generate_request_event(path_parameters={"daemonId": test_daemon_id})

        response = get_daemon_logs(event, None, test_daemon_service, test_auth_service)
        _, message = validate_response_forbidden(response)

        assert message == "Access denied"


class TestUpdateConfig:
    def test_update_config_ok(
        self,
        test_daemon_service,
        test_auth_service,
        test_session_factory,
        add_test_daemon,
        test_daemon_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        event = generate_request_event(
            path_parameters={"daemonId": test_daemon_id},
            body={
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            },
        )

        response = update_config(event, None, test_daemon_service, test_auth_service)
        _, _ = validate_response_ok(response)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.daemon_config["service_endpoint"] == test_service_endpoint
        assert daemon.daemon_config["service_credentials"] == test_service_credentials

    def test_update_config_incorrect_credentials_format(
        self,
        test_daemon_service,
        test_auth_service,
        add_test_daemon,
        test_daemon_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        del test_service_credentials[0]["location"]

        event = generate_request_event(
            path_parameters={"daemonId": test_daemon_id},
            body={
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            },
        )

        response = update_config(event, None, test_daemon_service, test_auth_service)
        _, message = validate_response_bad_request(response)

        assert (
            message
            == "Invalid service auth parameters! Must be 'key', 'value' and 'location' and not empty."
        )

    def test_update_config_no_daemon(
        self,
        test_daemon_service,
        test_auth_service,
        test_daemon_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        event = generate_request_event(
            path_parameters={"daemonId": test_daemon_id},
            body={
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            },
        )

        response = update_config(event, None, test_daemon_service, test_auth_service)
        _, message = validate_response_forbidden(response)

        assert message == "Access denied"

    def test_update_config_service_exists(
        self,
        test_daemon_service,
        test_auth_service,
        add_test_daemon_and_service,
        test_daemon_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        event = generate_request_event(
            path_parameters={"daemonId": test_daemon_id},
            body={
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            },
        )

        response = update_config(event, None, test_daemon_service, test_auth_service)
        _, message = validate_response_bad_request(response)

        assert message == "Config update is not available!"

    def test_update_config_unacceptable_status(
        self,
        test_daemon_service,
        test_auth_service,
        test_session_factory,
        add_test_account_balance,
        test_account_id,
        test_org_id,
        test_service_id,
        test_daemon_id,
        test_service_endpoint,
        test_service_credentials,
    ):
        event = generate_request_event(
            path_parameters={"daemonId": test_daemon_id},
            body={
                "serviceEndpoint": test_service_endpoint,
                "serviceCredentials": test_service_credentials,
            },
        )

        with session_scope(test_session_factory) as session:
            add_daemon(
                session,
                test_account_id,
                test_org_id,
                test_service_id,
                test_daemon_id,
                status=DaemonStatus.STARTING,
            )

        response = update_config(event, None, test_daemon_service, test_auth_service)
        _, message = validate_response_bad_request(response)

        assert message == "Config update is not available!"


class TestUpdateDaemonStatus:
    def test_update_daemon_status_first_time_ok(
        self,
        test_daemon_service,
        test_session_factory,
        add_test_daemon,
        test_daemon_id,
        test_org_id,
        test_service_id,
    ):
        # update status with null status_observed_at and status_resource_version fields
        test_status = "DOWN"
        test_observed_at = "2025-01-15T10:30:00.123456789Z"
        test_resource_version = "123"

        event = generate_request_event(
            orgId=test_org_id,
            serviceId=test_service_id,
            status=test_status,
            observedAt=test_observed_at,
            resourceVersion=test_resource_version,
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

    def test_update_daemon_status_not_first_time_ok(
        self,
        test_daemon_service,
        test_session_factory,
        add_test_account_balance,
        test_account_id,
        test_daemon_id,
        test_org_id,
        test_service_id,
    ):
        # update status with not null status_observed_at and status_resource_version fields
        test_status = "STARTING"
        test_observed_at = "2026-01-15T10:30:00.123456789Z"
        test_resource_version = "234"

        with session_scope(test_session_factory) as session:
            add_daemon(
                session,
                test_account_id,
                test_org_id,
                test_service_id,
                test_daemon_id,
                status_observed_at="2025-12-13T15:31:45.123456789Z",
                status_resource_version="123",
            )

        event = generate_request_event(
            orgId=test_org_id,
            serviceId=test_service_id,
            status=test_status,
            observedAt=test_observed_at,
            resourceVersion=test_resource_version,
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

    def test_update_daemon_status_same_resource_version_ok(
        self,
        test_daemon_service,
        test_session_factory,
        add_test_account_balance,
        test_account_id,
        test_daemon_id,
        test_org_id,
        test_service_id,
    ):
        current_status = "UP"
        current_observed_at = "2025-12-13T15:31:45.123456789Z"
        current_resource_version = "123"

        test_status = "STARTING"
        test_observed_at = "2026-01-15T10:30:00.123456789Z"
        test_resource_version = "123"

        with session_scope(test_session_factory) as session:
            add_daemon(
                session,
                test_account_id,
                test_org_id,
                test_service_id,
                test_daemon_id,
                status=current_status,
                status_observed_at=current_observed_at,
                status_resource_version=current_resource_version,
            )

        event = generate_request_event(
            orgId=test_org_id,
            serviceId=test_service_id,
            status=test_status,
            observedAt=test_observed_at,
            resourceVersion=test_resource_version,
        )
        queue_event = create_common_queue_event([event])
        update_daemon_status(queue_event, None, test_daemon_service)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.status.value == current_status
        assert daemon.status_observed_at == datetime.fromisoformat(current_observed_at).replace(
            microsecond=0, tzinfo=None
        )
        assert daemon.status_resource_version == current_resource_version

    def test_update_daemon_status_deprecated_event_ok(
        self,
        test_daemon_service,
        test_session_factory,
        add_test_account_balance,
        test_account_id,
        test_daemon_id,
        test_org_id,
        test_service_id,
    ):
        current_status = "UP"
        current_observed_at = "2025-12-13T15:31:45.123456789Z"
        current_resource_version = "123"

        test_status = "STARTING"
        test_observed_at = "2025-12-13T14:31:45.123456789Z"
        test_resource_version = "234"

        with session_scope(test_session_factory) as session:
            add_daemon(
                session,
                test_account_id,
                test_org_id,
                test_service_id,
                test_daemon_id,
                status=current_status,
                status_observed_at=current_observed_at,
                status_resource_version=current_resource_version,
            )

        event = generate_request_event(
            orgId=test_org_id,
            serviceId=test_service_id,
            status=test_status,
            observedAt=test_observed_at,
            resourceVersion=test_resource_version,
        )
        queue_event = create_common_queue_event([event])
        update_daemon_status(queue_event, None, test_daemon_service)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.status.value == current_status
        assert daemon.status_observed_at == datetime.fromisoformat(current_observed_at).replace(
            microsecond=0, tzinfo=None
        )
        assert daemon.status_resource_version == current_resource_version

    def test_update_daemon_status_no_daemon(
        self, test_daemon_service, test_org_id, test_service_id
    ):
        test_status = "DOWN"
        test_observed_at = "2025-01-15T10:30:00.123456789Z"
        test_resource_version = "123"

        event = generate_request_event(
            orgId=test_org_id,
            serviceId=test_service_id,
            status=test_status,
            observedAt=test_observed_at,
            resourceVersion=test_resource_version,
        )
        queue_event = create_common_queue_event([event])

        with pytest.raises(DaemonNotFoundForServiceException) as e:
            update_daemon_status(queue_event, None, test_daemon_service)

        assert e.type == DaemonNotFoundForServiceException
        assert (
            f"Daemon for service with org_id={test_org_id} and service_id={test_service_id} not found!"
            in str(e.value)
        )


class TestRedeployDaemonForcibly:
    def test_redeploy_daemon_forcibly_ok(
        self,
        test_daemon_service,
        test_session_factory,
        add_test_daemon,
        test_daemon_id,
    ):
        event = generate_request_event(path_parameters={"daemonId": test_daemon_id})

        response = redeploy_daemon_forcibly(event, None, test_daemon_service)
        validate_response_ok(response)

        with session_scope(test_session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, test_daemon_id)

        assert daemon.status == DaemonStatus.STARTING

    def test_redeploy_daemon_forcibly_no_daemon(
        self,
        test_daemon_service,
        test_daemon_id,
    ):
        event = generate_request_event(path_parameters={"daemonId": test_daemon_id})

        response = redeploy_daemon_forcibly(event, None, test_daemon_service)
        _, message = validate_response_not_found(response)

        assert message == f"Daemon with id {test_daemon_id} not found!"


class TestDaemonEndpoints:
    pass
    # def test_deploy_daemon_ok(self, test_daemon_service):
    #     pass
    #
    # def test_redeploy_all_daemons(self, test_daemon_service):
    #     pass
