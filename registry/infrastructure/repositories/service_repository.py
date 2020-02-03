from registry.domain.factory.service_factory import ServiceFactory
from registry.infrastructure.models.models import Service, ServiceGroup, ServiceReviewWorkflow, ServiceReviewHistory
from registry.infrastructure.repositories.base_repository import BaseRepository
from sqlalchemy import func


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
        total_count_of_services = self.session.query(func.count(Service.uuid)). \
            join(ServiceReviewWorkflow, ServiceReviewWorkflow.service_uuid == Service.uuid). \
            filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
            filter(Service.org_uuid == org_uuid).all()[0][0]
        self.session.commit()
        return total_count_of_services

    def check_service_id_within_organization(self, org_uuid, service_id):
        record_exist = self.session.query(func.count(Service.uuid)).filter(Service.org_uuid == org_uuid) \
            .filter(Service.service_id == service_id).all()[0][0]
        return record_exist

    def add_service(self, service_db_model):
        self.add_item(service_db_model)
