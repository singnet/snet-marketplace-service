from typing import Optional

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from deployer.domain.factory.hosted_service_factory import HostedServiceFactory
from deployer.domain.models.hosted_service import NewHostedServiceDomain, HostedServiceDomain
from deployer.infrastructure.models import HostedService, Daemon, HostedServiceStatus


class HostedServiceRepository:
    @staticmethod
    def create_hosted_service(session: Session, hosted_service: NewHostedServiceDomain):
        hosted_service_db = HostedService(
            id=hosted_service.id,
            daemon_id=hosted_service.daemon_id,
            status=hosted_service.status,
            github_account_name=hosted_service.github_account_name,
            github_repository_name=hosted_service.github_repository_name,
            last_commit_url=hosted_service.last_commit_url,
        )

        session.add(hosted_service_db)

    @staticmethod
    def update_hosted_service_status(
        session: Session,
        hosted_service_id: str,
        status: HostedServiceStatus,
        last_commit_url: str = None,
    ) -> None:
        update_values = {
            "status": status,
        }
        if last_commit_url is not None:
            update_values["last_commit_url"] = last_commit_url

        update_query = (
            update(HostedService)
            .where(HostedService.id == hosted_service_id)
            .values(**update_values)
        )

        session.execute(update_query)

    @staticmethod
    def get_hosted_service(
        session: Session, hosted_service_id: str
    ) -> Optional[HostedServiceDomain]:
        query = select(HostedService).where(HostedService.id == hosted_service_id)

        result = session.execute(query)

        hosted_service_db = result.scalar_one_or_none()
        if hosted_service_db is None:
            return None

        return HostedServiceFactory.hosted_service_from_db_model(hosted_service_db)

    @staticmethod
    def get_hosted_service_by_account_and_service(
        session: Session, account_id: str, hosted_service_id: str
    ) -> Optional[HostedServiceDomain]:
        query = (
            select(HostedService)
            .join(Daemon, Daemon.id == HostedService.daemon_id)
            .where(Daemon.account_id == account_id, HostedService.id == hosted_service_id)
            .limit(1)
        )

        result = session.execute(query)

        hosted_service_db = result.scalar_one_or_none()
        if hosted_service_db is None:
            return None

        return HostedServiceFactory.hosted_service_from_db_model(hosted_service_db)

    @staticmethod
    def search_hosted_service(
        session: Session, org_id: str, service_id: str
    ) -> Optional[HostedServiceDomain]:
        query = (
            select(HostedService)
            .join(Daemon, Daemon.id == HostedService.daemon_id)
            .where(Daemon.org_id == org_id, Daemon.service_id == service_id)
            .limit(1)
        )

        result = session.execute(query)

        hosted_service_db = result.scalar_one_or_none()
        if hosted_service_db is None:
            return None

        return HostedServiceFactory.hosted_service_from_db_model(hosted_service_db)
