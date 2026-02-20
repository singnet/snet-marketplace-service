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
    def __init__(
        self, session_factory=None, deployer_client=None, haas_client=None, boto_utils=None
    ):
        self.session_factory = DefaultSessionFactory if session_factory is None else session_factory
        self._deployer_client = DeployerClient() if deployer_client is None else deployer_client
        self._haas_client = HaaSClient() if haas_client is None else haas_client
        self._boto_utils = BotoUtils(REGION_NAME) if boto_utils is None else boto_utils

    def get_daemon(self, request: DaemonRequest) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)

        # In this case, the daemon will never be None, because otherwise the verification will not pass at the authorization stage earlier

        result = daemon.to_response(with_hosted_service=False)
        result.update(result["daemon"])
        del result["daemon"]

        return result

    def get_daemon_logs(self, request: DaemonRequest) -> List[str]:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
        # In this case, the daemon will never be None, because otherwise the verification will not pass at the authorization stage earlier

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
            if (
                daemon.status_resource_version is not None
                and daemon.status_resource_version == request.status_resource_version
            ):
                logger.exception(
                    f"The received event has the same resource version: {request.status_resource_version}. Skip."
                )
                return
            if (
                daemon.status_observed_at is not None
                and daemon.status_observed_at > request.status_observed_at.replace(tzinfo=None)
            ):
                logger.exception(
                    f"The received event is out of date: existing - {daemon.status_observed_at}, received - {request.status_observed_at}. Skip."
                )
                return

            DaemonRepository.update_daemon_status(
                session,
                daemon.id,
                DaemonStatus(request.status),
                request.status_observed_at,
                request.status_resource_version,
            )

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

        logger.info(f"(Re)Starting daemon id={daemon.id}, org_id={daemon.org_id}, service_id={daemon.service_id}")

        self._haas_client.deploy_daemon(
            org_id=daemon.org_id,
            service_id=daemon.service_id,
            daemon_config=daemon.daemon_config,
        )

        with session_scope(self.session_factory) as session:
            DaemonRepository.update_daemon_status(
                session,
                daemon_id,
                DaemonStatus.STARTING,
                daemon.status_observed_at,
                daemon.status_resource_version,
            )

        return {}

    def update_config(self, request: UpdateConfigRequest) -> dict:
        service_endpoint = request.service_endpoint
        service_credentials = request.service_credentials
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, request.daemon_id)
            # In this case, the daemon will never be None, because otherwise the verification will not pass at the authorization stage earlier

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

    def redeploy_daemon_forcibly(self, request: DaemonRequest) -> None:
        daemon_id = request.daemon_id

        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon(session, daemon_id)

        if daemon is None:
            raise DaemonNotFoundException(daemon_id)

        self._haas_client.deploy_daemon(
            org_id = daemon.org_id,
            service_id = daemon.service_id,
            daemon_config = daemon.daemon_config,
        )

        with session_scope(self.session_factory) as session:
            DaemonRepository.update_daemon_status(
                session,
                daemon_id,
                DaemonStatus.STARTING,
                daemon.status_observed_at,
                daemon.status_resource_version,
            )

        logger.info(f"Restarting daemon id={daemon.id}, org_id={daemon.org_id}, service_id={daemon.service_id}")
