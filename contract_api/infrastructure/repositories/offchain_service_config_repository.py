from sqlalchemy.exc import SQLAlchemyError
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from contract_api.infrastructure.models import OffchainServiceConfig as OffchainServiceConfigDBModel


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
