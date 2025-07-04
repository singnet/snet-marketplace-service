from dataclasses import dataclass
from datetime import datetime

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceMetadataDomain:
    service_row_id: int
    org_id: str
    service_id: str
    display_name: str
    description: str
    short_description: str
    url: str
    json: str
    model_hash: str
    encoding: str
    type: str
    mpe_address: str
    assets_url: dict
    assets_hash: dict
    service_rating: dict
    contributors: dict


@dataclass
class ServiceMetadataDomain(NewServiceMetadataDomain, BaseDomain):
    row_id: int
    demo_component_available: bool
    ranking: int
    created_on: datetime
    updated_on: datetime

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "displayName": self.display_name,
            "description": self.description,
            "shortDescription": self.short_description,
            "url": self.url,
            "rating": self.service_rating["rating"],
            "numberOfRatings": self.service_rating["total_users_rated"],
            "contributors": self.contributors,
        }

