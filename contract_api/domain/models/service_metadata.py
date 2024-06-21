from dataclasses import dataclass


@dataclass
class ServiceMetadataEntityModel:
    
    org_id: str
    service_id: str
    display_name: str
    description: str
    short_description: str
    demo_component_available: str
    url: str
    json: str
    model_ipfs_hash: str
    encoding: str
    type: str
    mpe_address: str
    assets_url: dict
    assets_hash: dict
    service_rating: dict
    ranking: int
    contributors: dict
