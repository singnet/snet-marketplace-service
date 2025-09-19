from dataclasses import dataclass
from datetime import datetime

from deployer.domain.models.base_domain import BaseDomain
from deployer.infrastructure.models import DeploymentStatus


@dataclass
class NewDaemonDomain:
    id: str
    account_id: str
    org_id: str
    service_id: str
    status: DeploymentStatus
    daemon_config: dict
    service_published: bool
    daemon_endpoint: str
    start_at: datetime
    end_at: datetime


@dataclass
class DaemonDomain(NewDaemonDomain, BaseDomain):
    def to_short_response(self):
        return {"id": self.id, "status": self.status.value, "endOn": self.end_at.isoformat()}

    def to_response(self) -> dict:
        result = super().to_response()
        del result["accountId"]
        return result
