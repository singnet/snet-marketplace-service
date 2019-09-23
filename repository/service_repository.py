from models import Service
from repository.base_repository import BaseRepository


class ServiceRepository(BaseRepository):

    def get_service_by_servcie_id_and_org_id(self, service_id, org_id, session=None):
        session = self.get_default_session(session)

        result = session.query(Service).filter(Service.service_id == service_id).\
            filter(Service.org_id == org_id).first()

        session.commit()

        return result
