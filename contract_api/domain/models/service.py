from dataclasses import dataclass
from datetime import datetime

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceDomain:
    org_id: str
    service_id: str
    hash_uri: str
    is_curated: bool


@dataclass
class ServiceDomain(NewServiceDomain, BaseDomain):
    row_id: int
    service_path: str
    service_email: str
    created_on: datetime
    updated_on: datetime

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
        }
