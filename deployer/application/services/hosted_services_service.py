from deployer.application.schemas.hosted_services_schemas import (
    HostedServiceRequest,
    UpdateHostedServiceStatusRequest,
    CheckGithubRepositoryRequest,
)
from deployer.exceptions import HostedServiceNotFoundException, RepositoryInstallationNotFoundException
from deployer.infrastructure.clients.github_api_client import GithubAPIClient
from deployer.infrastructure.clients.haas_client import HaaSClient
from deployer.infrastructure.db import DefaultSessionFactory, session_scope
from deployer.infrastructure.models import DeploymentStatus
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.hosted_service_repository import HostedServiceRepository


class HostedServicesService:
    def __init__(self):
        self.session_factory = DefaultSessionFactory
        self._haas_client = HaaSClient()
        self._github_client = GithubAPIClient()

    def get_hosted_service(self, request: HostedServiceRequest) -> dict:
        with session_scope(self.session_factory) as session:
            hosted_service = HostedServiceRepository.get_hosted_service(
                session, request.hosted_service_id
            )

        if hosted_service is None:
            raise HostedServiceNotFoundException(request.hosted_service_id)

        return hosted_service.to_response()

    def get_hosted_service_logs(self, request: HostedServiceRequest) -> list:
        with session_scope(self.session_factory) as session:
            hosted_service = HostedServiceRepository.get_hosted_service(
                session, request.hosted_service_id
            )
            if hosted_service is None:
                raise HostedServiceNotFoundException(request.hosted_service_id)
            daemon = DaemonRepository.get_daemon(session, hosted_service.daemon_id)

        hosted_service_logs = self._haas_client.get_hosted_service_logs(
            daemon.org_id, daemon.service_id
        )

        return hosted_service_logs

    def check_github_repository(self, request: CheckGithubRepositoryRequest) -> dict:
        result = self._github_client.check_repo_installation(
            request.account_name, request.repository_name
        )
        if result:
            return {"isInstalled": True}
        else:
            raise RepositoryInstallationNotFoundException(
                request.account_name, request.repository_name
            )

    def update_hosted_service_status(self, request: UpdateHostedServiceStatusRequest):
        with session_scope(self.session_factory) as session:
            hosted_service = HostedServiceRepository.get_hosted_service(
                session, request.hosted_service_id
            )
            if hosted_service is None:
                raise HostedServiceNotFoundException(request.hosted_service_id)

            new_status = DeploymentStatus(request.status.upper())
            HostedServiceRepository.update_hosted_service_status(
                session,
                request.hosted_service_id,
                new_status,
                self._build_commit_url(request.github_url, request.last_commit_url),
            )

    def deploy_service(self, request: HostedServiceRequest):
        pass

    def delete_service(self, request: HostedServiceRequest):
        pass

    @staticmethod
    def _build_commit_url(github_url: str, last_commit_url: str) -> str:
        return f"{github_url}/commit/{last_commit_url}"
