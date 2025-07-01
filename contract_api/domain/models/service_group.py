from dataclasses import dataclass
from datetime import datetime

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceGroupDomain:
    service_row_id: int
    org_id: str
    service_id: str
    group_id: str
    group_name: str
    free_call_signer_address: str
    free_calls: int
    pricing: dict


@dataclass
class ServiceGroupDomain(NewServiceGroupDomain, BaseDomain):
    row_id: str
    created_on: datetime
    updated_on: datetime

    def to_short_response(self) -> dict:
        return {
            "groupId": self.group_id,
            "groupName": self.group_name,
            "freeCallSignerAddress": self.free_call_signer_address,
            "freeCalls": self.free_calls,
            "pricing": self.pricing,
        }