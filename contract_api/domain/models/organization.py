from dataclasses import dataclass
from datetime import datetime

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewOrganizationDomain:
    org_id: str
    organization_name: str
    owner_address: str
    org_metadata_uri: str
    org_assets_url: dict
    is_curated: bool
    description: dict
    assets_hash: dict
    contacts: dict


@dataclass
class OrganizationDomain(NewOrganizationDomain, BaseDomain):
    row_id: int
    org_email: str
    created_on: datetime
    updated_on: datetime

    def to_short_response(self) -> dict:
        for contact in self.contacts:
            contact.update({"contactType": contact["contact_type"]})
        return {
            "orgId": self.org_id,
            "organizationName": self.organization_name,
            "orgImageUrl": self.org_assets_url["hero_image"],
            "contacts": self.contacts
        }


