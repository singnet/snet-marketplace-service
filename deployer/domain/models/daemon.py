from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from deployer.domain.models.base_domain import BaseDomain
from deployer.domain.models.hosted_service import HostedServiceDomain
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
    hosted_service: Optional[HostedServiceDomain] = None

    def to_response(self, remove_created_updated: bool = True, with_hosted_service: bool = True) -> dict:
        result = {
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "daemon": {
                "id": self.id,
                "status": self.status.value,
                "daemonConfig": self.daemon_config,
                "daemonEndpoint": self.daemon_endpoint,
            }
        }

        if with_hosted_service:
            result["hostedService"] = self.hosted_service.to_response() if self.hosted_service is not None else None

        return result

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "daemon": {
                "id": self.id,
                "status": self.status.value,
                "updatedAt": self.updated_at.isoformat()
            },
            "hostedService": self.hosted_service.to_short_response() if self.hosted_service is not None else None
        }
