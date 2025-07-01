from dataclasses import dataclass
from datetime import datetime

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceTagDomain:
    service_row_id: int
    org_id: str
    service_id: str
    tag_name: str


@dataclass
class ServiceTagDomain(NewServiceTagDomain, BaseDomain):
    row_id: int
    created_on: datetime
    updated_on: datetime
