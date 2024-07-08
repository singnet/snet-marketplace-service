from datetime import datetime as dt

from contract_api.infrastructure.models import Service, ServiceMetadata
from contract_api.infrastructure.models import OffchainServiceConfig
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from contract_api.domain.factory.service_factory import ServiceFactory
from sqlalchemy.exc import SQLAlchemyError

service_factory = ServiceFactory()


class ServiceRepository(BaseRepository):

    def get_service(self, org_id, service_id):
        service_db = self.session.query(Service). \
            filter(Service.org_id == org_id). \
            filter(Service.service_id == service_id).first()
        return service_factory.convert_service_db_model_to_entity_model(service_db) \
            if service_db else None

    @BaseRepository.write_ops
    def create_service(self, service):
        pass





class OffchainServiceConfigRepository(BaseRepository):
    pass

    def get_offchain_service_config(self, org_id, service_id):
        offchain_service_configs_db = self.session.query(OffchainServiceConfig). \
            filter(OffchainServiceConfig.org_id == org_id). \
            filter(OffchainServiceConfig.service_id == service_id). \
            all()
        offchain_service_config = ServiceFactory().convert_offchain_service_configs_db_model_to_entity_model(
            org_id=org_id,
            service_id=service_id,
            offchain_service_configs_db=offchain_service_configs_db
        )
        return offchain_service_config

    def save_offchain_service_attribute(self, offchain_service_attribute):
        attributes = offchain_service_attribute.attributes
        for key in attributes:
            parameter_name = key
            parameter_value = attributes[key]
            try:
                offchain_service_config_db = self.session.query(OffchainServiceConfig). \
                    filter(OffchainServiceConfig.org_id == offchain_service_attribute.org_id). \
                    filter(OffchainServiceConfig.service_id == offchain_service_attribute.service_id). \
                    filter(OffchainServiceConfig.parameter_name == parameter_name). \
                    first()
                if offchain_service_config_db:
                    offchain_service_config_db.parameter_value = parameter_value
                    offchain_service_config_db.updated_on=dt.utcnow()
                self.session.commit()
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e
            if not offchain_service_config_db:
                self.add_item(OffchainServiceConfig(
                    org_id=offchain_service_attribute.org_id,
                    service_id=offchain_service_attribute.service_id,
                    parameter_name=parameter_name,
                    parameter_value=parameter_value,
                    created_on=dt.utcnow(),
                    updated_on=dt.utcnow()
                ))
        return offchain_service_attribute
