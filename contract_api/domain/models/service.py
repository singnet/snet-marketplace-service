from dataclasses import dataclass
from domain.models.service_metadata import ServiceMetadata


@dataclass
class ServiceEntityModel:

    org_id: str
    service_id: str
    service_path: str
    ipfs_hash: str
    is_curated: int
    service_email: str
    service_metadata: ServiceMetadata = None
