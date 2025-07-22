from dataclasses import dataclass

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceDomain:
    org_id: str
    service_id: str
    hash_uri: str
    is_curated: bool


@dataclass
class ServiceDomain(NewServiceDomain, BaseDomain):
    service_path: str
    service_email: str

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
        }
