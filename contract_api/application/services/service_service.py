from typing import Dict, List
from common.logger import get_logger
from infrastructure.repositories.service_repository import ServiceRepository
from application.schema.service import GetServiceRequest
from contract_api.application.schema.service import AttributeNameEnum


logger = get_logger(__name__)


class ServiceService:

    def __init__(self):
        self.__service_repo = ServiceRepository()

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

        
