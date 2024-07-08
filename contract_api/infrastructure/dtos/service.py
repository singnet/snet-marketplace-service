from dataclasses import dataclass

@dataclass
class CreateServiceDto:
    org_id: str
    service_id: str
    service_path: str
    ipfs_hash: str
    is_curated: int