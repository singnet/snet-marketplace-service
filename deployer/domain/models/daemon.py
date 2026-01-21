from dataclasses import dataclass
from typing import Optional

from common.utils import dict_keys_to_camel_case
from deployer.domain.models.base_domain import BaseDomain
from deployer.domain.models.hosted_service import HostedServiceDomain
from deployer.infrastructure.models import DaemonStatus


@dataclass
class NewDaemonDomain:
    id: str
    account_id: str
    org_id: str
    service_id: str
    status: DaemonStatus
    daemon_config: dict
    daemon_endpoint: str


@dataclass
class DaemonDomain(NewDaemonDomain, BaseDomain):
    hosted_service: Optional[HostedServiceDomain] = None

    def to_response(
        self, remove_created_updated: bool = True, with_hosted_service: bool = True
    ) -> dict:
        result = {
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "daemon": {
                "id": self.id,
                "status": self.status.value,
                "daemonConfig": dict_keys_to_camel_case(self.daemon_config, recursively=True),
                "daemonEndpoint": self.daemon_endpoint,
                "updatedAt": self.updated_at.isoformat(),
            },
        }

        if with_hosted_service:
            result["hostedService"] = (
                self.hosted_service.to_response() if self.hosted_service is not None else None
            )

        return result

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "daemon": {
                "id": self.id,
                "status": self.status.value,
                "updatedAt": self.updated_at.isoformat(),
            },
            "hostedService": self.hosted_service.to_short_response()
            if self.hosted_service is not None
            else None,
        }
