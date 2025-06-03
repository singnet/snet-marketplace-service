import datetime as dt

from contract_api.infrastructure.models import Service as ServiceDB, ServiceMetadata as ServiceMetadataDB
from contract_api.infrastructure.models import OffchainServiceConfig
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from contract_api.domain.factory.service_factory import ServiceFactory
from sqlalchemy.exc import SQLAlchemyError

service_factory = ServiceFactory()


class ServiceRepository(BaseRepository):
    pass

    def get_service(self, org_id, service_id):
        try:
            service_db = self.session.query(ServiceDB). \
                filter(ServiceDB.org_id == org_id). \
                filter(ServiceDB.service_id == service_id). \
                first()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not service_db:
            return None
        return service_factory.convert_service_db_model_to_entity_model(service_db)

    def create_or_update_service(self, service):
        current_datetime = dt.datetime.now(dt.UTC)
        try:
            service_db = self.session.query(ServiceDB). \
                filter(ServiceDB.org_id == service.org_id). \
                filter(ServiceDB.service_id == service.service_id). \
                first()
            if service_db:
                service_db.hash_uri = service.hash_uri,
                service_db.is_curated = service.is_curated,
                service_db.service_email = service.service_email
                service_db.row_updated = current_datetime
                service_db.service_metadata.display_name = service.service_metadata.display_name
                service_db.service_metadata.description = service.service_metadata.description
                service_db.service_metadata.short_description = service.service_metadata.short_description
                service_db.service_metadata.url = service.service_metadata.url
                service_db.service_metadata.json = service.service_metadata.json
                service_db.service_metadata.model_hash = service.service_metadata.model_hash
                service_db.service_metadata.encoding = service.service_metadata.encoding
                service_db.service_metadata.type = service.service_metadata.type
                service_db.service_metadata.mpe_address = service.service_metadata.mpe_address
                service_db.service_metadata.assets_url = service.service_metadata.assets_url
                service_db.service_metadata.assets_hash = service.service_metadata.assets_hash
                service_db.service_metadata.service_rating = service.service_metadata.service_rating
                service_db.service_metadata.ranking = service.service_metadata.ranking
                service_db.service_metadata.demo_component_available = service.service_metadata.demo_component_available
                service_db.service_metadata.contributors = service.service_metadata.contributors
                service_db.service_metadata.row_updated = current_datetime
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not service_db:
            self.add_item(ServiceDB(
                org_id=service.org_id,
                service_id=service.service_id,
                service_path=None,
                hash_uri=service.hash_uri,
                is_curated=service.is_curated,
                service_email=service.service_email,
                row_created=current_datetime,
                row_updated=current_datetime,
                service_metadata=ServiceMetadataDB(
                    org_id=service.service_metadata.org_id,
                    service_id=service.service_metadata.service_id,
                    display_name=service.service_metadata.display_name,
                    description=service.service_metadata.description,
                    short_description=service.service_metadata.short_description,
                    demo_component_available=service.service_metadata.demo_component_available,
                    url=service.service_metadata.url,
                    json=service.service_metadata.json,
                    model_hash=service.service_metadata.model_hash,
                    encoding=service.service_metadata.encoding,
                    type=service.service_metadata.type,
                    mpe_address=service.service_metadata.mpe_address,
                    assets_url=service.service_metadata.assets_url,
                    assets_hash=service.service_metadata.assets_hash,
                    service_rating=service.service_metadata.service_rating,
                    ranking=service.service_metadata.ranking,
                    contributors=service.service_metadata.contributors,
                    row_created=current_datetime,
                    row_updated=current_datetime
                )
            ))


class OffchainServiceConfigRepository(BaseRepository):
    pass

    def get_offchain_service_config(self, org_id, service_id):
        try:
            offchain_service_configs_db = self.session.query(OffchainServiceConfig). \
                filter(OffchainServiceConfig.org_id == org_id). \
                filter(OffchainServiceConfig.service_id == service_id). \
                all()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        offchain_service_config = ServiceFactory().convert_offchain_service_configs_db_model_to_entity_model(
            org_id=org_id,
            service_id=service_id,
            offchain_service_configs_db=offchain_service_configs_db
        )
        return offchain_service_config

    def save_offchain_service_attribute(self, offchain_service_attribute):
        attributes = offchain_service_attribute.attributes
        current_datetime = dt.datetime.now(dt.UTC)
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
                    offchain_service_config_db.updated_on=current_datetime
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
                    created_on=current_datetime,
                    updated_on=current_datetime
                ))
        return offchain_service_attribute
