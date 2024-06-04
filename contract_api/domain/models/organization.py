from dataclasses import dataclass
from typing import Dict


@dataclass
class OrganizationEntityModel:
    org_id: int
    organization_name: str
    owner_address: str
    org_metadata_uri: str
    org_email: str
    org_assets_url: str
    is_currated: int
    description: str
    assets_hash: Dict[str, str]
    contacts: Dict[str, str]

