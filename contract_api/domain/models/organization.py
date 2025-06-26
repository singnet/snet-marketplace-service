from dataclasses import dataclass
from datetime import datetime


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
class OrganizationDomain(NewOrganizationDomain):
    row_id: int
    org_email: str
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "organization_name": self.organization_name,
            "owner_address": self.owner_address,
            "org_metadata_uri": self.org_metadata_uri,
            "org_email": self.org_email,
            "org_assets_url": self.org_assets_url,
            "is_curated": self.is_curated,
            "description": self.description,
            "assets_hash": self.assets_hash,
            "contacts": self.contacts
        }

    def to_short_response(self) -> dict:
        for contact in self.contacts:
            contact.update({"contactType": contact["contact_type"]})
        return {
            "orgId": self.org_id,
            "organizationName": self.organization_name,
            "orgImageUrl": self.org_assets_url["hero_image"],
            "contacts": self.contacts
        }


