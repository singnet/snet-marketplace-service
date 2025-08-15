from dataclasses import dataclass
from datetime import datetime

from deployer.domain.models.base_domain import BaseDomain
from deployer.infrastructure.models import ClaimingPeriodStatus


@dataclass
class NewClaimingPeriodDomain:
    daemon_id: str
    start_on: datetime
    end_on: datetime
    status: ClaimingPeriodStatus


@dataclass
class ClaimingPeriodDomain(NewClaimingPeriodDomain, BaseDomain):
    id: int