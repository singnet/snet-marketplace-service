from datetime import datetime as dt

from contract_api.infrastructure.models import Service as ServiceDB, ServiceMetadata as ServiceMetadataDB
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.infrastructure.models import OffchainServiceConfig as OffchainServiceConfigDBModel
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
        try:
            service_db = self.session.query(ServiceDB). \
                filter(ServiceDB.org_id == service.org_id). \
                filter(ServiceDB.service_id == service.service_id). \
                first()
            if service_db:
                service_db.ipfs_hash = service.ipfs_hash,
                service_db.is_curated = service.is_curated,
                service_db.service_email = service.service_email
                service_db.row_updated = dt.utcnow()
                service_db.service_metadata.display_name = service.service_metadata.display_name
                service_db.service_metadata.description = service.service_metadata.description
                service_db.service_metadata.short_description = service.service_metadata.short_description
                service_db.service_metadata.url = service.service_metadata.url
                service_db.service_metadata.json = service.service_metadata.json
                service_db.service_metadata.model_ipfs_hash = service.service_metadata.model_ipfs_hash
                service_db.service_metadata.encoding = service.service_metadata.encoding
                service_db.service_metadata.type = service.service_metadata.type
                service_db.service_metadata.mpe_address = service.service_metadata.mpe_address
                service_db.service_metadata.assets_url = service.service_metadata.assets_url
                service_db.service_metadata.assets_hash = service.service_metadata.assets_hash
                service_db.service_metadata.service_rating = service.service_metadata.service_rating
                service_db.service_metadata.ranking = service.service_metadata.ranking
                service_db.service_metadata.demo_component_available = service.service_metadata.demo_component_available
                service_db.service_metadata.contributors = service.service_metadata.contributors
                service_db.service_metadata.row_updated = dt.utcnow()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not service_db:
            self.add_item(ServiceDB(
                org_id=service.org_id,
                service_id=service.service_id,
                service_path=None,
                ipfs_hash=service.ipfs_hash,
                is_curated=service.is_curated,
                service_email=service.service_email,
                row_created=dt.utcnow(),
                row_updated=dt.utcnow,
                service_metadata=ServiceMetadataDB(
                    org_id=service.service_metadata.org_id,
                    service_id=service.service_metadata.service_id,
                    display_name=service.service_metadata.display_name,
                    description=service.service_metadata.description,
                    short_description=service.service_metadata.short_description,
                    demo_component_available=service.service_metadata.demo_component_available,
                    url=service.service_metadata.url,
                    json=service.service_metadata.json,
                    model_ipfs_hash=service.service_metadata.model_ipfs_hash,
                    encoding=service.service_metadata.encoding,
                    type=service.service_metadata.type,
                    mpe_address=service.service_metadata.mpe_address,
                    assets_url=service.service_metadata.assets_url,
                    assets_hash=service.service_metadata.assets_hash,
                    service_rating=service.service_metadata.service_rating,
                    ranking=service.service_metadata.ranking,
                    contributors=service.service_metadata.contributors,
                    row_created=dt.utcnow(),
                    row_updated=dt.utcnow()
                )
            ))


class OffchainServiceConfigRepository(BaseRepository):
    pass

    def get_offchain_service_config(self, org_id, service_id):
        try:
            offchain_service_config_db = self.session.query(OffchainServiceConfigDBModel). \
                filter(OffchainServiceConfigDBModel.org_id == org_id). \
                filter(OffchainServiceConfigDBModel.service_id == service_id). \
                all()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        offchain_service_config = ServiceFactory().convert_offchain_service_config_db_model_to_entity_model(
            org_id=org_id,
            service_id=service_id,
            offchain_service_configs_db=offchain_service_config_db
        )
        return offchain_service_config
