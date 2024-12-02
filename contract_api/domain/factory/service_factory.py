from datetime import datetime as dt
from typing import Dict, List
from contract_api.domain.models.demo_component import DemoComponentEntityModel
from contract_api.domain.factory.organization_factory import OrganizationFactory
from contract_api.domain.models.service import (
    ServiceEntityModel,
    ServiceMetadataEntityModel,
    ServiceMediaEntityModel,
    ServiceFullInfoEntityModel
)
from contract_api.domain.models.offchain_service_attribute import OffchainServiceAttributeEntityModel
from contract_api.infrastructure.models import (
    Service,
    ServiceMetadata,
    ServiceMedia,
    OffchainServiceConfig,
    Organization
)


class ServiceFactory:

    @staticmethod
    def convert_service_db_model_to_entity_model(service_db: Service) -> ServiceEntityModel:
        if not service_db:
            return None
        return ServiceEntityModel(
            org_id=service_db.org_id,
            service_id=service_db.service_id,
            service_path=service_db.service_path,
            ipfs_hash=service_db.ipfs_hash,
            is_curated=service_db.is_curated,
            service_email=service_db.service_email,
            service_metadata=ServiceFactory.convert_service_metadata_db_model_to_entity_model(
                service_db.service_metadata)
        )

    @staticmethod
    def convert_service_metadata_db_model_to_entity_model(service_metadata_db: ServiceMetadata) -> ServiceMetadataEntityModel:
        if not service_metadata_db:
            return None
        return ServiceMetadataEntityModel(
            org_id=service_metadata_db.org_id,
            service_id=service_metadata_db.service_id,
            display_name=service_metadata_db.display_name,
            description=service_metadata_db.description,
            short_description=service_metadata_db.short_description,
            demo_component_available=service_metadata_db.demo_component_available,
            url=service_metadata_db.url,
            json=service_metadata_db.json,
            model_ipfs_hash=service_metadata_db.model_ipfs_hash,
            encoding=service_metadata_db.encoding,
            type=service_metadata_db.type,
            mpe_address=service_metadata_db.mpe_address,
            assets_url=service_metadata_db.assets_url,
            assets_hash=service_metadata_db.assets_hash,
            service_rating=service_metadata_db.service_rating,
            ranking=service_metadata_db.ranking,
            contributors=service_metadata_db.contributors
        )

    @staticmethod
    def convert_service_media_db_model_to_entity_model(service_media_db: ServiceMedia) -> ServiceMediaEntityModel:
        if not service_media_db:
            return None
        return ServiceMediaEntityModel(
            org_id=service_media_db.org_id,
            service_id=service_media_db.service_id,
            url=service_media_db.url,
            order=service_media_db.order,
            file_type=service_media_db.file_type,
            asset_type=service_media_db.asset_type,
            alt_text=service_media_db.alt_text,
            ipfs_url=service_media_db.ipfs_url
        )

    @staticmethod
    def convert_offchain_service_configs_db_model_to_entity_model(
        org_id: str,
        service_id: str,
        offchain_service_configs_db: OffchainServiceConfig
    ) -> OffchainServiceAttributeEntityModel:
        attributes = {}
        for offchain_service_config_db in offchain_service_configs_db:
            parameter_name = offchain_service_config_db.parameter_name
            if offchain_service_config_db.parameter_name == "demo_component_url":
                attributes.update(
                    {"demo_component_last_modified": dt.isoformat(offchain_service_config_db.updated_on)}
                )
            if offchain_service_config_db.parameter_name == "demo_component_required":
                parameter_value = int(offchain_service_config_db.parameter_value)
            else:
                parameter_value = offchain_service_config_db.parameter_value
            attributes.update({parameter_name: parameter_value})
        return OffchainServiceAttributeEntityModel(
            org_id=org_id,
            service_id=service_id,
            attributes=attributes
        )

    @staticmethod
    def create_demo_component_entity_model(offchain_attributes: Dict[str, str]):
        return DemoComponentEntityModel(
            demo_component_url=offchain_attributes.get("demo_component_url", ""),
            demo_component_status=offchain_attributes.get("demo_component_status", ""),
            demo_component_required=offchain_attributes.get("demo_component_required", "")
        )
    
    @staticmethod
    def create_service_full_info_entity_model(
        service_db: Service,
        service_metadata_db: ServiceMetadata,
        organization_db: Organization,
        service_media_db: ServiceMedia,
        tags: List[str],
        is_available: int,
    ) -> ServiceFullInfoEntityModel:
        if not service_db:
            return None
        return ServiceFullInfoEntityModel(
            service=ServiceFactory.convert_service_db_model_to_entity_model(service_db),
            service_metadata=ServiceFactory.convert_service_metadata_db_model_to_entity_model(service_metadata_db),
            organization=OrganizationFactory.convert_to_organization_entity_model_from_db_model(organization_db),
            service_media=ServiceFactory.convert_service_media_db_model_to_entity_model(service_media_db),
            tags=tags,
            is_available=is_available
        )
