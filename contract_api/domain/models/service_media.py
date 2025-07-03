from dataclasses import dataclass
from datetime import datetime

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceMediaDomain:
    service_row_id: int
    org_id: str
    service_id: str
    url: str
    order: int
    file_type: str
    asset_type: str
    alt_text: str
    hash_uri: str


@dataclass
class ServiceMediaDomain(NewServiceMediaDomain, BaseDomain):
    row_id: str
    created_on: datetime
    updated_on: datetime

    def to_short_response(self) -> dict:
        return {
            "url": self.url,
            "assetType": self.asset_type,
        }
