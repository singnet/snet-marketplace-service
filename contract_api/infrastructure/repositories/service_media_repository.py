from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.infrastructure.models import ServiceMedia
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from sqlalchemy.exc import SQLAlchemyError
import datetime as dt


class ServiceMediaRepository(BaseRepository):

    def get_service_media(self, org_id, service_id):
        try:
            service_media = self.session.query(ServiceMedia) \
                .filter(ServiceMedia.org_id == org_id).filter(ServiceMedia.service_id == service_id) \
                .all()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        service_media_list = []
        for media in service_media:
            service_media_list.append(ServiceFactory.convert_service_media_db_model_to_entity_model(media))
        return service_media_list

    def create_service_media(self, org_id, service_id, service_media):
        current_datetime = dt.datetime.now(dt.UTC)
        self.add_item(ServiceMedia(
            service_row_id=service_media.service_row_id,
            org_id=org_id,
            service_id=service_id,
            url=service_media.url,
            order=service_media.order,
            file_type=service_media.file_type,
            asset_type=service_media.asset_type,
            alt_text=service_media.alt_text,
            hash_uri=service_media.hash_uri,
            created_on=current_datetime,
            updated_on=current_datetime
        ))

    def delete_service_media(self, org_id, service_id, asset_types=None, file_types=None):
        try:
            service_media_query = self.session.query(ServiceMedia) \
                .filter(ServiceMedia.org_id == org_id).filter(ServiceMedia.service_id == service_id)
            if file_types and type(file_types) == list:
                service_media_query = service_media_query.filter(ServiceMedia.file_type.in_(file_types))
            if asset_types and type(asset_types) == list:
                service_media_query = service_media_query.filter(ServiceMedia.asset_type.in_(asset_types))
            service_media_query.delete(synchronize_session='fetch')
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def update_service_media(self, org_id, service_id, service_media_list, asset_types):
        try:
            self.delete_service_media(org_id=org_id, service_id=service_id, asset_types=asset_types)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        for media in service_media_list:
            self.create_service_media(org_id=org_id, service_id=service_id, service_media=media)
