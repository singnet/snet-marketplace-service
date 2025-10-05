from sqlalchemy import update
from sqlalchemy.orm import Session

from deployer.domain.models.hosted_service import NewHostedServiceDomain
from deployer.infrastructure.models import HostedService, DeploymentStatus


class HostedServiceRepository:
    @staticmethod
    def create_hosted_service(session: Session, hosted_service: NewHostedServiceDomain):
        hosted_service_db = HostedService(
            id=hosted_service.id,
            daemon_id=hosted_service.daemon_id,
            status=hosted_service.status,
            github_url=hosted_service.github_url,
            last_commit_url=hosted_service.last_commit_url,
        )

        session.add(hosted_service_db)

    @staticmethod
    def update_hosted_service_status(session: Session, hosted_service_id: str, status: DeploymentStatus):
        update_query = update(HostedService).where(HostedService.id == hosted_service_id).values(status=status)

        session.execute(update_query)