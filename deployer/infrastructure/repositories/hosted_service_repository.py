from sqlalchemy.orm import Session

from deployer.domain.models.hosted_service import NewHostedServiceDomain
from deployer.infrastructure.models import HostedService


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