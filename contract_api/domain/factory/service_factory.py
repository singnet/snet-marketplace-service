from typing import Sequence
from dataclasses import fields

from contract_api.domain.models.demo_component import DemoComponent
from contract_api.domain.models.service import ServiceDomain
from contract_api.domain.models.service_endpoint import ServiceEndpointDomain
from contract_api.domain.models.service_group import ServiceGroupDomain
from contract_api.domain.models.service_media import ServiceMediaDomain
from contract_api.domain.models.offchain_service_attribute import OffchainServiceConfigDomain
from contract_api.domain.models.service_metadata import ServiceMetadataDomain, NewServiceMetadataDomain
from contract_api.domain.models.service_tag import ServiceTagDomain
from contract_api.infrastructure.models import ServiceTags, ServiceMedia, Service, ServiceMetadata, ServiceGroup, \
    ServiceEndpoint, OffchainServiceConfig


class ServiceFactory:

    @staticmethod
    def service_tag_from_db_model(
            service_tag_db_model: ServiceTags
    ) -> ServiceTagDomain:
        return ServiceTagDomain(
            row_id=service_tag_db_model.row_id,
            service_row_id = service_tag_db_model.service_row_id,
            org_id=service_tag_db_model.org_id,
            service_id=service_tag_db_model.service_id,
            tag_name=service_tag_db_model.tag_name,
            created_on=service_tag_db_model.created_on,
            updated_on=service_tag_db_model.updated_on
        )

    @staticmethod
    def service_tags_from_db_model_list(
            service_tag_db_model_list: Sequence[ServiceTags]
    ) -> list[ServiceTagDomain]:
        result = []
        for service_tag_db in service_tag_db_model_list:
            result.append(ServiceFactory.service_tag_from_db_model(service_tag_db))
        return result

    @staticmethod
    def service_media_from_db_model(
            service_media_db_model: ServiceMedia
    ) -> ServiceMediaDomain:
        return ServiceMediaDomain(
            row_id=service_media_db_model.row_id,
            service_row_id=service_media_db_model.service_row_id,
            org_id=service_media_db_model.org_id,
            service_id=service_media_db_model.service_id,
            url=service_media_db_model.url,
            order=service_media_db_model.order,
            file_type=service_media_db_model.file_type,
            asset_type=service_media_db_model.asset_type,
            alt_text=service_media_db_model.alt_text,
            hash_uri=service_media_db_model.hash_uri,
            created_on=service_media_db_model.created_on,
            updated_on=service_media_db_model.updated_on
        )

    @staticmethod
    def service_media_from_db_model_list(
            service_media_db_model_list: Sequence[ServiceMedia]
    ) -> list[ServiceMediaDomain]:
        result = []
        for service_media_db in service_media_db_model_list:
            result.append(ServiceFactory.service_media_from_db_model(service_media_db))
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
    def services_from_db_model_list(
            service_db_model_list: Sequence[Service]
    ) -> list[ServiceDomain]:
        result = []
        for service_db in service_db_model_list:
            result.append(ServiceFactory.service_from_db_model(service_db))
        return result

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
        for name, value in demo_component.to_short_dict().items():
            result.append(OffchainServiceConfigDomain(
                row_id=0, # dummy
                org_id="", # dummy
                service_id="", # dummy
                parameter_name = name,
                parameter_value = value
            ))
        return result

    @staticmethod
    def service_metadata_from_metadata_dict(
            metadata_dict: dict,
            **kwargs
    ) -> NewServiceMetadataDomain:

        def default_field(_field):
            if _field.type == int:
                return 0
            elif _field.type == str:
                return ""
            elif _field.type == dict:
                return {}

        attributes = {}
        for field in fields(NewServiceMetadataDomain):
            if field.name in kwargs:
                attributes[field.name] = kwargs[field.name]
            else:
                attributes[field.name] = metadata_dict.get(field.name, default_field(field))

        return NewServiceMetadataDomain(**attributes)

