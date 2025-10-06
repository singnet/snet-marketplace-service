from typing import Iterable, List

from deployer.domain.models.hosted_service import HostedServiceDomain
from deployer.infrastructure.models import HostedService


class HostedServiceFactory:
    @staticmethod
    def hosted_service_from_db_model(hosted_service_db_model: HostedService) -> HostedServiceDomain:
        return HostedServiceDomain(
            id=hosted_service_db_model.id,
            daemon_id=hosted_service_db_model.daemon_id,
            status=hosted_service_db_model.status,
            github_url=hosted_service_db_model.github_url,
            last_commit_url=hosted_service_db_model.last_commit_url,
            created_at=hosted_service_db_model.created_at,
            updated_at=hosted_service_db_model.updated_at,
        )

    @staticmethod
    def hosted_services_from_db_model(
        hosted_services_db_model: Iterable[HostedService],
    ) -> List[HostedServiceDomain]:
        return [
            HostedServiceFactory.hosted_service_from_db_model(hosted_service_db_model)
            for hosted_service_db_model in hosted_services_db_model
        ]
