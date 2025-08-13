from dataclasses import dataclass
from datetime import datetime

from deployer.domain.models.base_domain import BaseDomain
from deployer.domain.models.order import OrderDomain
from deployer.infrastructure.models import DaemonStatus


@dataclass
class NewDaemonDomain:
    id: str
    account_id: str
    org_id: str
    service_id: str
    status: DaemonStatus
    daemon_config: dict
    start_on: datetime | None = None
    end_on: datetime | None = None


@dataclass
class DaemonDomain(NewDaemonDomain, BaseDomain):
    orders: list[OrderDomain] | None = None

    def to_short_response(self):
        return {
            "id": self.id,
            "status": self.status.value,
            "startOn": self.start_on,
            "endOn": self.end_on
        }