from dataclasses import dataclass
from datetime import datetime

from deployer.domain.models.base_domain import BaseDomain
from deployer.infrastructure.models import ClaimingPeriodStatus


@dataclass
class NewClaimingPeriodDomain:
    daemon_id: str
    start_at: datetime
    end_at: datetime
    status: ClaimingPeriodStatus


@dataclass
class ClaimingPeriodDomain(NewClaimingPeriodDomain, BaseDomain):
    id: int

    def to_daemon_response(self):
        response = {
            "lastClaimedAt": self.end_at.isoformat(),
        }
        if self.status == ClaimingPeriodStatus.ACTIVE:
            response["status"] = "CLAIMING"

        return response
