from models import Service, ServiceMetadata
from repository.base_repository import BaseRepository


class ServiceMetadataRepository(BaseRepository):

    def get_service_metatdata_by_servcie_id_and_org_id(self, service_id, org_id, session=None):
        session = self.get_default_session(session)

        result = session.query(ServiceMetadata).filter(ServiceMetadata.service_id == service_id).\
            filter(ServiceMetadata.org_id == org_id).first()

        return result

    def update_assets_url(self, service_id, org_id, new_assets_url, session=None):
        session = self.get_default_session(session)
        result = session.query(ServiceMetadata).filter(ServiceMetadata.service_id == service_id). \
            filter(ServiceMetadata.org_id == org_id).first()
        result.assets_url = new_assets_url

        session.commit()
