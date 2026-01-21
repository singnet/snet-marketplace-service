from typing import List, Tuple

from common.boto_utils import BotoUtils
from common.logger import get_logger
from deployer.application.schemas.daemon_schemas import (
    DaemonRequest,
    UpdateConfigRequest,
    UpdateDaemonStatusRequest,
)
from deployer.config import REGION_NAME
from deployer.exceptions import (
    DaemonNotFoundException,
    UpdateConfigNotAvailableException,
    DaemonNotFoundForServiceException,
)
from deployer.infrastructure.clients.deployer_client import DeployerClient
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DaemonStatus
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

    def get_daemon_logs(self, request: DaemonRequest) -> List[str]:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
        if daemon is None:
            raise DaemonNotFoundException(request.daemon_id)

        daemon_logs = self._haas_client.get_daemon_logs(daemon.org_id, daemon.service_id)

        return daemon_logs

    def download_daemon_logs(self, request: DaemonRequest) -> Tuple[str, str]:
        daemon_logs = self.get_daemon_logs(request)

        return "\n".join(daemon_logs), f"daemon_{request.daemon_id}_logs.txt"

    def redeploy_all_daemons(self) -> dict:
        with session_scope(self.session_factory) as session:
            daemon_ids = DaemonRepository.get_all_daemon_ids(session, status=DaemonStatus.UP)
            for daemon_id in daemon_ids:
                self._deployer_client.deploy_daemon(daemon_id, asynchronous=True)
        return {}

    def update_daemon_status(self, request: UpdateDaemonStatusRequest):
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(
                session, org_id=request.org_id, service_id=request.service_id
            )
            if daemon is None:
                raise DaemonNotFoundForServiceException(request.org_id, request.service_id)

            new_status = DaemonStatus(request.status)
            DaemonRepository.update_daemon_status(session, daemon.id, new_status)

        logger.info(f"Status for daemon {daemon.id} updated to {request.status}")

    def deploy_daemon(self, request: DaemonRequest):
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

        if daemon is None:
            raise DaemonNotFoundException(daemon_id)

        if daemon.status not in [DaemonStatus.INIT, DaemonStatus.UP]:
            logger.exception(f"Daemon {daemon_id} is not in INIT or UP status")
            return {}

        logger.info(f"(Re)Starting daemon {daemon.id}")

        self._haas_client.deploy_daemon(
            org_id=daemon.org_id,
            service_id=daemon.service_id,
            daemon_config=daemon.daemon_config,
        )

        return {}

    def update_config(self, request: UpdateConfigRequest) -> dict:
        service_endpoint = request.service_endpoint
        service_credentials = request.service_credentials
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
            if daemon is None:
                raise DaemonNotFoundException(request.daemon_id)
            if daemon.hosted_service is not None or daemon.status == DaemonStatus.STARTING:
                raise UpdateConfigNotAvailableException()

            daemon_config = daemon.daemon_config
            if service_endpoint:
                daemon_config["service_endpoint"] = service_endpoint
            if service_credentials:
                daemon_config["service_credentials"] = service_credentials

            DaemonRepository.update_daemon_config(session, request.daemon_id, daemon_config)

            if daemon.status == DaemonStatus.UP:
                self._deployer_client.deploy_daemon(request.daemon_id, asynchronous=True)

        return {}
