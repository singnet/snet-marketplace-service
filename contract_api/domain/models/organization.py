from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrganizationDomain:
    row_id: int
    org_id: str
    organization_name: str
    owner_address: str
    org_metadata_uri: str
    org_email: str
    org_assets_url: dict
    is_curated: bool
    description: dict
    assets_hash: dict
    contacts: dict
    created_on: datetime
    updated_on: datetime

    def to_response(self):
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
