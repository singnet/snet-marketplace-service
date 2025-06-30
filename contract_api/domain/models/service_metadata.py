from dataclasses import dataclass
from datetime import datetime


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
class ServiceMetadataDomain(NewServiceMetadataDomain):
    row_id: int
    demo_component_available: bool
    ranking: int
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "display_name": self.display_name,
            "description": self.description,
            "short_description": self.short_description,
            "demo_component_available": self.demo_component_available,
            "url": self.url,
            "json": self.json,
            "model_hash": self.model_hash,
            "encoding": self.encoding,
            "type": self.type,
            "mpe_address": self.mpe_address,
            "assets_url": self.assets_url,
            "assets_hash": self.assets_hash,
            "service_rating": self.service_rating,
            "ranking": self.ranking,
            "contributors": self.contributors,
        }

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "displayName": self.display_name,
            "description": self.description,
            "shortDescription": self.short_description,
            "url": self.url,
            "rating": self.service_rating["rating"],
            "numberOfRatings": self.service_rating["number_of_ratings"],
            "contributors": self.contributors,
        }

