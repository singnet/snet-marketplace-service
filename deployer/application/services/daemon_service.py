from datetime import datetime, UTC, timedelta

from common.boto_utils import BotoUtils
from common.logger import get_logger
from deployer.application.schemas.daemon_schemas import (
    DaemonRequest,
    UpdateConfigRequest,
    UpdateDaemonStatusRequest,
)
from deployer.config import (
    MAX_DAEMON_STARTING_TIME_IN_SECONDS,
    DAEMON_CHECK_INTERVAL_IN_SECONDS,
    REGION_NAME,
    CHECK_DAEMON_STATUS_TOPIC_ARN,
    MAX_DAEMON_RESTARTING_TIME_IN_SECONDS,
)
from deployer.exceptions import (
    DaemonNotFoundException,
    UpdateConfigNotAvailableException,
)
from deployer.infrastructure.clients.deployer_client import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient, HaaSDaemonStatus
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DeploymentStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository


logger = get_logger(__name__)


class DaemonService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._deployer_client = DeployerClient()
        self._haas_client = HaaSClient()
        self._boto_utils = BotoUtils(REGION_NAME)

    def get_daemon(self, request: DaemonRequest) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
            if daemon is None:
                raise DaemonNotFoundException(request.daemon_id)

        result = daemon.to_response(with_hosted_service=False)

        return result

    def get_daemon_logs(self, request: DaemonRequest) -> list:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
        if daemon is None:
            raise DaemonNotFoundException(request.daemon_id)

        daemon_logs = self._haas_client.get_daemon_logs(daemon.org_id, daemon.service_id)

        return daemon_logs

    def redeploy_all_daemons(self) -> dict:
        with session_scope(self.session_factory) as session:
            daemon_ids = DaemonRepository.get_all_daemon_ids(session, status=DeploymentStatus.UP)
            for daemon_id in daemon_ids:
                self._deployer_client.deploy_daemon(daemon_id, asynchronous=True)
        return {}

    def check_daemon_status(self, request: UpdateDaemonStatusRequest):
        daemon_id = request.daemon_id
        generate_event = request.generate_event

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            status = daemon.status

            if status not in [DeploymentStatus.STARTING, DeploymentStatus.UP]:
                logger.info(f"Daemon {daemon_id} is not in STARTING or UP status")
                if generate_event:
                    self._push_check_status_event(
                        daemon_id, generate_event=True, seconds=DAEMON_CHECK_INTERVAL_IN_SECONDS
                    )
                return

            haas_daemon_status, started_at = self._haas_client.check_daemon(
                daemon.org_id, daemon.service_id
            )

            current_time = datetime.now(UTC)
            if (
                status == DeploymentStatus.STARTING
                and generate_event
                and daemon.updated_at + timedelta(seconds=MAX_DAEMON_RESTARTING_TIME_IN_SECONDS)
                >= current_time
            ):
                logger.info(f"Daemon {daemon_id} is still starting")
                if generate_event:
                    self._push_check_status_event(
                        daemon_id, generate_event=True, seconds=DAEMON_CHECK_INTERVAL_IN_SECONDS
                    )
                return

            if haas_daemon_status == HaaSDaemonStatus.DOWN:
                DaemonRepository.update_daemon_status(session, daemon_id, DeploymentStatus.ERROR)
            elif status == DeploymentStatus.STARTING:
                DaemonRepository.update_daemon_status(session, daemon_id, DeploymentStatus.UP)

        if generate_event:
            self._push_check_status_event(
                daemon_id, generate_event=True, seconds=DAEMON_CHECK_INTERVAL_IN_SECONDS
            )

    def deploy_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

            if daemon is None:
                raise DaemonNotFoundException(daemon_id)

            if daemon.status not in [DeploymentStatus.INIT, DeploymentStatus.UP]:
                logger.exception(f"Daemon {daemon_id} is not in INIT or UP status")
                return {}

            if daemon.status == DeploymentStatus.INIT:
                self._haas_client.deploy_daemon(
                    org_id=daemon.org_id,
                    service_id=daemon.service_id,
                    daemon_config=daemon.daemon_config,
                )
                self._push_check_status_event(
                    daemon_id, generate_event=False, seconds=MAX_DAEMON_STARTING_TIME_IN_SECONDS
                )
            else:
                self._haas_client.redeploy_daemon(
                    org_id=daemon.org_id,
                    service_id=daemon.service_id,
                    daemon_config=daemon.daemon_config,
                )
                self._push_check_status_event(
                    daemon_id, generate_event=False, seconds=MAX_DAEMON_RESTARTING_TIME_IN_SECONDS
                )
            DaemonRepository.update_daemon_status(session, daemon_id, DeploymentStatus.STARTING)

        return {}

    def delete_daemon(self, request: DaemonRequest):
        pass

    def redeploy_daemon(self, request: DaemonRequest):
        pass

    def update_config(self, request: UpdateConfigRequest) -> dict:
        service_endpoint = request.service_endpoint
        service_credentials = request.service_credentials
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
            if daemon is None:
                raise DaemonNotFoundException(request.daemon_id)
            if daemon.hosted_service is not None or daemon.status != DeploymentStatus.UP:
                raise UpdateConfigNotAvailableException()

            daemon_config = daemon.daemon_config
            if service_endpoint:
                daemon_config["service_endpoint"] = service_endpoint
            if service_credentials:
                daemon_config["service_credentials"] = service_credentials

            DaemonRepository.update_daemon_config(session, request.daemon_id, daemon_config)

            if daemon.status == DeploymentStatus.UP:
                self._deployer_client.deploy_daemon(request.daemon_id, asynchronous=True)

        return {}

    def _push_check_status_event(
        self, daemon_id: str, generate_event: bool = True, seconds: int = 0
    ):
        self._boto_utils.publish_data_to_sns_topic(
            topic_arn=CHECK_DAEMON_STATUS_TOPIC_ARN,
            payload={"daemon_id": daemon_id, "generate_event": generate_event},
            delay_seconds=seconds,
        )
