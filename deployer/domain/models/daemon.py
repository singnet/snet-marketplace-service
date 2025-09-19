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
    daemon_endpoint: str


@dataclass
class DaemonDomain(NewDaemonDomain, BaseDomain):
    def to_response(self, remove_created_updated: bool = False) -> dict:
        result = super().to_response()
        del result["accountId"]
        return result
