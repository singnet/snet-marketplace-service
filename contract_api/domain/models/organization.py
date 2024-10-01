from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class OrganizationEntityModel:
    org_id: str
    organization_name: str
    owner_address: str
    org_metadata_uri: str
    org_email: str
    org_assets_url: str
    is_currated: int
    description: str
    assets_hash: Dict[str, str]
    contacts: Dict[str, str]


@dataclass(frozen=True)
class OrganizationGroupEntityModel:
    org_id: str
    group_id: str
    group_name: str
    payment: Dict[str, str]

    def to_dict(self):
        return {
            "org_id": self.org_id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "payment": self.payment
        }
