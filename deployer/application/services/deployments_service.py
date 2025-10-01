from typing import List

from common.logger import get_logger
from common.utils import generate_uuid
from deployer.application.schemas.deployments_schemas import InitiateDeploymentRequest, SearchDeploymentsRequest
from deployer.config import DEFAULT_DAEMON_STORAGE_TYPE
from deployer.domain.models.daemon import NewDaemonDomain
from deployer.domain.models.hosted_service import NewHostedServiceDomain
from deployer.exceptions import DaemonAlreadyExistsException
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DeploymentStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.hosted_service_repository import HostedServiceRepository
from deployer.utils import get_daemon_endpoint


logger = get_logger(__name__)


class DeploymentsService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._haas_client = HaaSClient()

    def initiate_deployment(self, request: InitiateDeploymentRequest, account_id: str) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, request.org_id, request.service_id)

            if daemon is not None:
                raise DaemonAlreadyExistsException(request.org_id, request.service_id)

            daemon_id = generate_uuid()

            daemon_config = {"payment_channel_storage_type": DEFAULT_DAEMON_STORAGE_TYPE.value}
            if request.only_daemon:
                daemon_config["is_service_hosted"] = False
                daemon_config["service_endpoint"] = request.service_endpoint
                if request.service_credentials is not None:
                    daemon_config["service_credentials"] = request.service_credentials
            else:
                daemon_config["is_service_hosted"] = True
                daemon_config["service_endpoint"] = ""

            DaemonRepository.create_daemon(
                session,
                NewDaemonDomain(
                    id=daemon_id,
                    account_id=account_id,
                    org_id=request.org_id,
                    service_id=request.service_id,
                    status=DeploymentStatus.INIT,
                    daemon_config=daemon_config,
                    daemon_endpoint=get_daemon_endpoint(request.org_id, request.service_id),
                )
            )

            if not request.only_daemon:
                HostedServiceRepository.create_hosted_service(
                    session,
                    NewHostedServiceDomain(
                        id=generate_uuid(),
                        daemon_id=daemon_id,
                        status=DeploymentStatus.INIT,
                        github_url=request.github_url,
                        last_commit_url="",
                    )
                )

        return {}

    def get_user_deployments(self, account_id: str) -> List[dict]:
        with session_scope(self.session_factory) as session:
            daemons = DaemonRepository.get_user_daemons(session, account_id)
        return [daemon.to_short_response() for daemon in daemons]

    def search_deployments(self, request: SearchDeploymentsRequest):
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.search_daemon(session, request.org_id, request.service_id)
        if daemon is None:
            return {"daemon": {}, "hostedService": {}}
        return daemon.to_response()

    def get_public_key(self) -> dict:
        public_key = self._haas_client.get_public_key()
        return {"publicKey": public_key}

    def process_registry_event(self):
        pass
