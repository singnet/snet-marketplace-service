from registry.domain.factory.service_factory import ServiceFactory
from registry.infrastructure.models.models import Service, ServiceGroup, ServiceReviewWorkflow, ServiceReviewHistory
from registry.infrastructure.repositories.base_repository import BaseRepository


class ServiceRepository(BaseRepository):
    def get_services_for_organization(self, org_uuid, payload):
        raw_services_data = self.session.query(Service, ServiceReviewWorkflow). \
            join(ServiceReviewWorkflow, ServiceReviewWorkflow.service_uuid == Service.uuid). \
            filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
            filter(Service.org_uuid == org_uuid). \
            order_by(getattr(getattr(Service, payload["sort_by"]), payload["order_by"])()). \
            slice(payload["offset"], payload["limit"]).all()

        services = []
        for service in raw_services_data:
            services.append(ServiceFactory().convert_service_db_model_to_entity_model(service).to_dict())
        self.session.commit()
        return services

    def get_total_count_of_services_for_organization(self, org_uuid, payload):
        raw_services_data = self.session.query(Service, ServiceReviewWorkflow). \
            join(ServiceReviewWorkflow, ServiceReviewWorkflow.service_uuid == Service.uuid). \
            filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
            filter(Service.org_uuid == org_uuid).all()
        self.session.commit()
        return len(raw_services_data)
