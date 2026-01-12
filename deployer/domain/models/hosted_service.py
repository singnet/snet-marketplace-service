from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain
from deployer.infrastructure.models import HostedServiceStatus as Status


@dataclass
class NewHostedServiceDomain:
    id: str
    daemon_id: str
    status: Status
    github_account_name: str
    github_repository_name: str
    last_commit_url: str


@dataclass
class HostedServiceDomain(NewHostedServiceDomain, BaseDomain):
    def to_response(self, remove_created_updated: bool = True) -> dict:
        result = super().to_response(remove_created_updated)
        del result["daemonId"]
        if result["status"] not in ["INIT", "UP", "DOWN", "ERROR"]:
            result["status"] = "STARTING"
        return result

    def to_short_response(self) -> dict:
        status = self.status
        if status not in [Status.INIT, Status.UP, Status.DOWN, Status.ERROR]:
            status = "STARTING"
        else:
            status = status.value
        return {
            "id": self.id,
            "status": status,
            "updatedAt": self.updated_at.isoformat(),
        }
