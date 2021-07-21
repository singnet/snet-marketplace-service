from contract_api.domain.models.offchain_service_attribute import OffchainServiceAttribute
from contract_api.infrastructure.repositories.service_repository import OffchainServiceConfigRepository

offchain_service_config_repo = OffchainServiceConfigRepository()


class RegistryService:
    def __init__(self, org_id, service_id):
        self.org_id = org_id
        self.service_id = service_id

    def save_offchain_service_attribute(self, attributes):
        offchain_service_attribute = OffchainServiceAttribute(org_id=self.org_id, service_id=self.service_id,
                                                              attributes=attributes)
        offchain_service_attribute = offchain_service_config_repo.save_offchain_service_attribute(offchain_service_attribute)
        return offchain_service_attribute.to_dict()
