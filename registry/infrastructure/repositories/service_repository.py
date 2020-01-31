from registry.domain.factory.service_factory import ServiceFactory
from registry.infrastructure.models.models import Service, ServiceGroup, ServiceReviewWorkflow, ServiceReviewHistory
from registry.infrastructure.repositories.base_repository import BaseRepository


class ServiceRepository(BaseRepository):
    def get_services_for_organization(self, org_uuid, payload):
        services = self.session.query(Service, ServiceReviewWorkflow). \
            join(ServiceReviewWorkflow, ServiceReviewWorkflow.service_uuid == Service.uuid). \
            filter(getattr(Service, payload["search_attribute"]) == payload["search_string"]). \
            filter(Service.org_uuid == org_uuid).\
            order_by(getattr(getattr(Service, payload["sort_by"]), payload["order_by"])).\
            slice(payload["offset"], payload["limit"]).all()
