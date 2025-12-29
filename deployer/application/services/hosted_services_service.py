from deployer.application.schemas.hosted_services_schemas import (
    HostedServiceRequest,
    UpdateHostedServiceStatusRequest,
    CheckGithubRepositoryRequest,
)
from deployer.exceptions import HostedServiceNotFoundException
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

    def get_hosted_service(self, request: HostedServiceRequest) -> dict:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon_by_hosted_service(session, request.hosted_service_id)
            if daemon is None:
                raise HostedServiceNotFoundException(hosted_service_id=request.hosted_service_id)
            hosted_service = daemon.hosted_service
            if hosted_service is None:
                raise HostedServiceNotFoundException(hosted_service_id=request.hosted_service_id)

        result = hosted_service.to_response(remove_created_updated=False)
        result["orgId"] = daemon.org_id
        result["serviceId"] = daemon.service_id

        return result

    def get_hosted_service_logs(self, request: HostedServiceRequest) -> list:
        with session_scope(self.session_factory) as session:
            daemon = DaemonRepository.get_daemon_by_hosted_service(session, request.hosted_service_id)
            if daemon is None or daemon.hosted_service is None:
                raise HostedServiceNotFoundException(hosted_service_id = request.hosted_service_id)

        hosted_service_logs = self._haas_client.get_hosted_service_logs(
            daemon.org_id, daemon.service_id
        )

        return hosted_service_logs

    def check_github_repository(self, request: CheckGithubRepositoryRequest) -> dict:
        is_installed = GithubAPIClient.check_repo_installation(
            request.account_name, request.repository_name
        )
        result = {"isInstalled": is_installed}
        if not is_installed:
            result["message"] = (
                f"The application is not installed in the repository with "
                f"account name {request.account_name} and repository name "
                f"{request.repository_name}, or the account and/or repository "
                f"name does not exist"
            )

        return result

    def update_hosted_service_status(self, request: UpdateHostedServiceStatusRequest):
        with session_scope(self.session_factory) as session:
            hosted_service = HostedServiceRepository.search_hosted_service(
                session, request.org_id, request.service_id
            )
            if hosted_service is None:
                raise HostedServiceNotFoundException(hosted_service_id=request.hosted_service_id)

            new_status = DeploymentStatus(request.status)
            HostedServiceRepository.update_hosted_service_status(
                session,
                request.hosted_service_id,
                new_status,
                GithubAPIClient.make_commit_url(
                    hosted_service.github_account_name,
                    hosted_service.github_repository_name,
                    request.commit_hash,
                ),
            )

    def delete_service(self, request: HostedServiceRequest):
        pass
