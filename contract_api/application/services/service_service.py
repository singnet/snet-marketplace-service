import json
from typing import Dict, List
from common.logger import get_logger
from infrastructure.repositories.service_repository import ServiceRepository, OffchainServiceConfigRepository
from infrastructure.repositories.organization_repository import OrganizationRepository
from application.schema.service import GetServiceRequest
from contract_api.application.schema.service import AttributeNameEnum
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.domain.models.service import ServiceMetadataEntityModel


logger = get_logger(__name__)


class ServiceService:

    def __init__(self):
        self.__service_repo = ServiceRepository()
        self.__offchain_service_config_repo = OffchainServiceConfigRepository()
        self.__organization_repo = OrganizationRepository()

    def get_services(self, get_services_request: GetServiceRequest) -> dict:
        services, total_count = self.__service_repo.get_services(get_services_request)
        return {
            "total_count": total_count,
            "offset": get_services_request.offset,
            "limit": get_services_request.limit,
            "result": [service.to_dict() for service in services]
        }

    def get_services_filter(self, attribute: AttributeNameEnum) -> List[Dict[str, str]]:
        services_attribute = self.__service_repo.get_services_by_attribute_name(attribute)
        return [
            {
                "key": service_by_attribute.key,
                "value": service_by_attribute.value
            }
            for service_by_attribute in services_attribute
        ]

    def __prepare_offchain_service_attributes(self, org_id: int, service_id: int) -> dict:
        offchain_attributes = {}
        offchain_service_config = self.__offchain_service_config_repo.get_offchain_service_config(
            org_id=org_id,
            service_id=service_id
        )
        offchain_attributes_db = offchain_service_config.attributes
        demo_component_required = offchain_attributes_db.get("demo_component_required", 0)
        demo_component = ServiceFactory().create_demo_component_entity_model(offchain_service_config.attributes)
        demo_component = demo_component.to_dict()
        # prepare format
        demo_last_modified = offchain_attributes_db.get("demo_component_last_modified", "")
        demo_component.update({"demo_component_last_modified": demo_last_modified if demo_last_modified else ""})
        offchain_attributes.update({"demo_component_required": demo_component_required})
        offchain_attributes.update({"demo_component": demo_component})
        return offchain_attributes       
