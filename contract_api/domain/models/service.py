from dataclasses import dataclass
from typing import List
from contract_api.domain.models.organization import OrganizationEntityModel


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class ServiceEntityModel:

    org_id: str
    service_id: str
    service_path: str
    ipfs_hash: str
    is_curated: int
    service_email: str
    service_metadata: ServiceMetadataEntityModel = None

    def to_dict(self):
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "display_name": self.service_metadata.display_name,
            "description": self.service_metadata.description,
            "url": self.service_metadata.url,
            "json": self.service_metadata.json,
            "model_ipfs_hash": self.service_metadata.model_ipfs_hash,
            "encoding": self.service_metadata.encoding,
            "type": self.service_metadata.type,
            "mpe_address": self.service_metadata.mpe_address,
            "service_rating": self.service_metadata.service_rating,
            "ranking": self.service_metadata.ranking,
            "contributors": self.service_metadata.contributors,
            "short_description": self.service_metadata.short_description,
        }


@dataclass
class ServiceMediaEntityModel:
    
    org_id: str
    service_id: str
    url: str
    order: int
    file_type: str
    asset_type: str
    alt_text: str
    ipfs_url: str

    def to_dict(self):
        return {
            "service_row_id": self._service_row_id,
            "org_id": self._org_id,
            "service_id": self._service_id,
            "url": self._url,
            "order": self._order,
            "file_type": self._file_type,
            "asset_type": self._asset_type,
            "alt_text": self._alt_text
        }


@dataclass(frozen=True)
class ServiceFullInfoEntityModel:

    service: ServiceEntityModel
    service_metadata: ServiceMetadataEntityModel
    service_media: ServiceMediaEntityModel
    organization: OrganizationEntityModel
    is_available: int
    tags: List[str]

    def to_dict(self):
        return {
            "org_id": self.service.org_id,
            "service_id": self.service.service_id,
            "display_name": self.service_metadata.display_name,
            "description": self.service_metadata.description,
            "url": self.service_metadata.url,
            "json": self.service_metadata.json,
            "model_ipfs_hash": self.service_metadata.model_ipfs_hash,
            "encoding": self.service_metadata.encoding,
            "type": self.service_metadata.type,
            "mpe_address": self.service_metadata.mpe_address,
            "service_rating": self.service_metadata.service_rating,
            "ranking": self.service_metadata.ranking,
            "contributors": self.service_metadata.contributors,
            "short_description": self.service_metadata.short_description,
            "organization_name": self.organization.organization_name,
            "org_assets_url": self.organization.org_assets_url,
            "contacts": self.organization.contacts,
            "tags": self.tags,
            "is_available": self.is_available,
            "media": {
                "org_id": self.service_media.org_id,
                "service_id": self.service_media.service_id,
                "file_type": self.service_media.file_type,
                "asset_type": self.service_media.asset_type,
                "url": self.service_media.url,
                "alt_text": self.service_media.alt_text,
                "order": self.service_media.order,
            }
        }