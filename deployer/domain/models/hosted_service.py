from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain
from deployer.infrastructure.models import DeploymentStatus


@dataclass
class NewHostedServiceDomain:
    id: str
    daemon_id: str
    status: DeploymentStatus
    github_account_name: str
    github_repository_name: str
    last_commit_url: str


@dataclass
class HostedServiceDomain(NewHostedServiceDomain, BaseDomain):
    def to_response(self, remove_created_updated: bool = True) -> dict:
        result = super().to_response(remove_created_updated)
        del result["daemonId"]
        return result

    def to_short_response(self) -> dict:
        return {
            "id": self.id,
            "status": self.status.value,
            "updatedAt": self.updated_at.isoformat(),
        }
