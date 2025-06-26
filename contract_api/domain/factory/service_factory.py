from typing import Sequence

from contract_api.domain.models.demo_component import DemoComponent
from contract_api.domain.models.service import ServiceDomain
from contract_api.domain.models.service_endpoint import ServiceEndpointDomain
from contract_api.domain.models.service_group import ServiceGroupDomain
from contract_api.domain.models.service_media import ServiceMediaDomain
from contract_api.domain.models.offchain_service_attribute import OffchainServiceAttribute, OffchainServiceConfigDomain
from contract_api.domain.models.service_metadata import ServiceMetadataDomain
from contract_api.domain.models.service_tag import ServiceTagDomain
from contract_api.infrastructure.models import ServiceTags, ServiceMedia, Service, ServiceMetadata, ServiceGroup, \
    ServiceEndpoint, OffchainServiceConfig


class ServiceFactory:

    @staticmethod
    def service_tags_from_db_model(
            service_tag_db_model_list: Sequence[ServiceTags]
    ) -> list[ServiceTagDomain]:
        result = []
        for service_tag_db in service_tag_db_model_list:
            result.append(ServiceTagDomain(
                row_id=service_tag_db.row_id,
                org_id=service_tag_db.org_id,
                service_id=service_tag_db.service_id,
                tag_name=service_tag_db.tag_name,
                created_on=service_tag_db.created_on,
                updated_on=service_tag_db.updated_on
            ))
        return result

    @staticmethod
    def service_media_from_db_model(
            service_media_db_model_list: Sequence[ServiceMedia]
    ) -> list[ServiceMediaDomain]:
        result = []
        for service_media_db in service_media_db_model_list:
            result.append(ServiceMediaDomain(
                row_id=service_media_db.row_id,
                service_row_id=service_media_db.service_row_id,
                org_id=service_media_db.org_id,
                service_id=service_media_db.service_id,
                url=service_media_db.url,
                order=service_media_db.order,
                file_type=service_media_db.file_type,
                asset_type=service_media_db.asset_type,
                alt_text=service_media_db.alt_text,
                hash_uri=service_media_db.hash_uri,
                created_on=service_media_db.created_on,
                updated_on=service_media_db.updated_on
            ))
        return result

    @staticmethod
    def service_from_db_model(
            service_db_model: Service
    ) -> ServiceDomain:
        return ServiceDomain(
            row_id=service_db_model.row_id,
            org_id=service_db_model.org_id,
            service_id=service_db_model.service_id,
            service_path=service_db_model.service_path,
            hash_uri=service_db_model.hash_uri,
            is_curated=service_db_model.is_curated,
            service_email=service_db_model.service_email,
            created_on = service_db_model.created_on,
            updated_on = service_db_model.updated_on
        )

    @staticmethod
    def service_metadata_from_db_model(
            service_metadata_db_model: ServiceMetadata
    ) -> ServiceMetadataDomain:
        return ServiceMetadataDomain(
            row_id=service_metadata_db_model.row_id,
            service_row_id=service_metadata_db_model.service_row_id,
            org_id=service_metadata_db_model.org_id,
            service_id=service_metadata_db_model.service_id,
            display_name=service_metadata_db_model.display_name,
            description=service_metadata_db_model.description,
            short_description=service_metadata_db_model.short_description,
            demo_component_available=service_metadata_db_model.demo_component_available,
            url=service_metadata_db_model.url,
            json=service_metadata_db_model.json,
            model_hash=service_metadata_db_model.model_hash,
            encoding=service_metadata_db_model.encoding,
            type=service_metadata_db_model.type,
            mpe_address=service_metadata_db_model.mpe_address,
            assets_url=service_metadata_db_model.assets_url,
            assets_hash=service_metadata_db_model.assets_hash,
            service_rating=service_metadata_db_model.service_rating,
            ranking=service_metadata_db_model.ranking,
            contributors=service_metadata_db_model.contributors,
            created_on = service_metadata_db_model.created_on,
            updated_on = service_metadata_db_model.updated_on
        )

    @staticmethod
    def service_group_from_db_model(
            service_group_db_model: ServiceGroup
    ) -> ServiceGroupDomain:
        return ServiceGroupDomain(
            row_id=service_group_db_model.row_id,
            service_row_id = service_group_db_model.service_row_id,
            org_id=service_group_db_model.org_id,
            service_id=service_group_db_model.service_id,
            group_id=service_group_db_model.group_id,
            group_name=service_group_db_model.group_name,
            free_call_signer_address = service_group_db_model.free_call_signer_address,
            free_calls = service_group_db_model.free_calls,
            pricing = service_group_db_model.pricing,
            created_on = service_group_db_model.created_on,
            updated_on = service_group_db_model.updated_on
        )

    @staticmethod
    def service_endpoint_from_db_model(
            service_endpoint_db_model: ServiceEndpoint
    ) -> ServiceEndpointDomain:
        return ServiceEndpointDomain(
            row_id=service_endpoint_db_model.row_id,
            service_row_id=service_endpoint_db_model.service_row_id,
            org_id=service_endpoint_db_model.org_id,
            service_id=service_endpoint_db_model.service_id,
            group_id = service_endpoint_db_model.group_id,
            endpoint=service_endpoint_db_model.endpoint,
            is_available=service_endpoint_db_model.is_available,
            last_check_timestamp=service_endpoint_db_model.last_check_timestamp,
            next_check_timestamp = service_endpoint_db_model.next_check_timestamp,
            failed_status_count = service_endpoint_db_model.failed_status_count,
            created_on = service_endpoint_db_model.created_on,
            updated_on = service_endpoint_db_model.updated_on
        )

    @staticmethod
    def offchain_service_configs_from_db_model_list(
            offchain_service_configs_db_model_list: Sequence[OffchainServiceConfig]
    ) -> list[OffchainServiceConfigDomain]:
        result = []
        for offchain_service_config_db_model in offchain_service_configs_db_model_list:
            result.append(OffchainServiceConfigDomain(
                row_id=offchain_service_config_db_model.row_id,
                org_id=offchain_service_config_db_model.org_id,
                service_id=offchain_service_config_db_model.service_id,
                parameter_name = offchain_service_config_db_model.parameter_name,
                parameter_value = offchain_service_config_db_model.parameter_value
            ))
        return result

    @staticmethod
    def offchain_service_configs_from_demo_component(
            demo_component: DemoComponent
    ) -> list[OffchainServiceConfigDomain]:
        result = []
        for name, value in demo_component.to_dict().items():
            result.append(OffchainServiceConfigDomain(
                row_id=0, # dummy
                org_id="", # dummy
                service_id="", # dummy
                parameter_name = name,
                parameter_value = value
            ))
        return result

    @staticmethod
    def convert_service_db_model_to_entity_model(service_db):
        if not service_db:
            return None
        return Service(
            row_id=service_db.row_id,
            org_id=service_db.org_id,
            service_id=service_db.service_id,
            service_path=service_db.service_path,
            hash_uri=service_db.hash_uri,
            is_curated=service_db.is_curated,
            service_email=service_db.service_email,
            service_metadata=ServiceFactory.convert_service_metadata_db_model_to_entity_model(
                service_db.service_metadata)
        )

    @staticmethod
    def convert_service_metadata_db_model_to_entity_model(service_metadata_db):
        if not service_metadata_db:
            return None
        return ServiceMetadata(
            service_row_id=service_metadata_db.service_row_id,
            org_id=service_metadata_db.org_id,
            service_id=service_metadata_db.service_id,
            display_name=service_metadata_db.display_name,
            description=service_metadata_db.description,
            short_description=service_metadata_db.short_description,
            demo_component_available=service_metadata_db.demo_component_available,
            url=service_metadata_db.url,
            json=service_metadata_db.json,
            model_hash=service_metadata_db.model_hash,
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
    def convert_service_media_db_model_to_entity_model(service_media_db):
        if not service_media_db:
            return None
        return ServiceMedia(
            service_row_id=service_media_db.service_row_id,
            org_id=service_media_db.org_id,
            service_id=service_media_db.service_id,
            url=service_media_db.url,
            order=service_media_db.order,
            file_type=service_media_db.file_type,
            asset_type=service_media_db.asset_type,
            alt_text=service_media_db.alt_text,
            hash_uri=service_media_db.hash_uri
        )

    @staticmethod
    def convert_offchain_service_configs_db_model_to_entity_model(org_id, service_id, offchain_service_configs_db):
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
        return OffchainServiceAttribute(
            org_id=org_id,
            service_id=service_id,
            attributes=attributes
        )

    @staticmethod
    def create_demo_component_domain_model(offchain_attributes):
        return DemoComponent(
            demo_component_url=offchain_attributes.get("demo_component_url", ""),
            demo_component_status=offchain_attributes.get("demo_component_status", ""),
            demo_component_required=offchain_attributes.get("demo_component_required", "")
        )
