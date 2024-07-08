from dataclasses import dataclass
from typing import Dict


@dataclass
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


@dataclass
class OrganizationGroupEntityModel:
    org_id: str
    group_id: str
    group_name: str
    payment: Dict[str, str]
