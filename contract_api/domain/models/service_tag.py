from dataclasses import dataclass

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceTagDomain:
    service_row_id: int
    org_id: str
    service_id: str
    tag_name: str


@dataclass
class ServiceTagDomain(NewServiceTagDomain, BaseDomain):
    pass
