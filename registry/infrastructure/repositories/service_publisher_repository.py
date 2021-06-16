from datetime import datetime as dt

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from registry.constants import ServiceStatus
from registry.domain.factory.service_factory import ServiceFactory
from registry.infrastructure.models import Service, ServiceGroup, ServiceState, ServiceReviewHistory, Organization, \
    ServiceComment
from registry.infrastructure.repositories.base_repository import BaseRepository


class ServicePublisherRepository(BaseRepository):
    def get_services_for_organization(self, org_uuid, payload):
        try:
            raw_services_data = self.session.query(Service). \
                filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
                filter(Service.org_uuid == org_uuid). \
                order_by(getattr(getattr(Service, payload["sort_by"]), payload["order_by"])()). \
                slice(payload["offset"], payload["limit"]).all()

            services = []
            for service in raw_services_data:
                services.append(ServiceFactory().convert_service_db_model_to_entity_model(service).to_dict())
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return services

    def get_total_count_of_services_for_organization(self, org_uuid, payload):
        try:
            total_count_of_services = self.session.query(func.count(Service.uuid)). \
                filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
                filter(Service.org_uuid == org_uuid).all()[0][0]
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return total_count_of_services

    def check_service_id_within_organization(self, org_uuid, service_id):
        try:
            record_exist = self.session.query(func.count(Service.uuid)).filter(Service.org_uuid == org_uuid) \
                .filter(Service.service_id == service_id).all()[0][0]
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return record_exist

    def add_service(self, service, username):
        service_db_model = ServiceFactory().convert_service_entity_model_to_db_model(username, service)
        self.add_item(service_db_model)

    def save_service(self, username, service, state):
        service_group_db_model = [ServiceFactory().convert_service_group_entity_model_to_db_model(group) for group in
                                  service.groups]
        try:
            self.session.query(ServiceGroup).filter(ServiceGroup.org_uuid == service.org_uuid).filter(
                ServiceGroup.service_uuid == service.uuid).delete(synchronize_session='fetch')
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        try:
            service_record = self.session.query(Service).filter(Service.org_uuid == service.org_uuid).filter(
                Service.uuid == service.uuid).first()
            service_record.display_name = service.display_name
            service_record.service_id = service.service_id
            service_record.metadata_uri = service.metadata_uri
            service_record.proto = service.proto
            service_record.short_description = service.short_description
            service_record.description = service.description
            service_record.project_url = service.project_url
            service_record.assets = service.assets
            service_record.rating = service.rating
            service_record.ranking = service.ranking
            service_record.contributors = service.contributors
            service_record.tags = service.tags
            service_record.mpe_address = service.mpe_address
            service_record.updated_on = dt.utcnow()
            service_record.groups = service_group_db_model
            service_record.service_state.state = state
            service_record.service_state.transaction_hash = service.service_state.transaction_hash
            service_record.service_state.updated_by = username
            service_record.service_state.updated_on = dt.utcnow()
            service_entity_model = ServiceFactory().convert_service_db_model_to_entity_model(service_record)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return service_entity_model

    def get_service_for_given_service_uuid(self, org_uuid, service_uuid):
        try:
            service_db = self.session.query(Service).filter(Service.org_uuid == org_uuid).filter(
                Service.uuid == service_uuid).first()
            service = ServiceFactory().convert_service_db_model_to_entity_model(service_db)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return service

    def add_service_review(self, org_uuid, service_uuid, payload):
        self.add_item(
            ServiceReviewHistory(
                org_uuid=org_uuid,
                service_uuid=service_uuid,
                reviewed_service_data=payload["service_metadata"],
                state="",
                reviewed_by=payload["reviewed_by"],
                reviewed_on=payload["reviewed_by"],
                created_on=payload["created_on"],
                updated_on=payload["updated_on"]
            )
        )

    def get_all_services_eligible_for_approval_atleast_once(self, status):
        pass

    def get_all_services_review_data(self):
        services_review_db = self.session.query(ServiceReviewHistory).all()
        services_review = [ServiceFactory.convert_service_review_history_entity_model_to_db_model(service_review_db) for
                           service_review_db in services_review_db]
        self.session.commit()
        return services_review

    def get_service_for_given_service_id_and_org_id(self, org_id, service_id):
        try:
            organization = self.session.query(Organization).filter(Organization.org_id == org_id).first()
            if not organization:
                raise Exception(f"No organization found for org_id:{org_id} service_id:{service_id}")
            org_uuid = organization.uuid
            service_db = self.session.query(Service).filter(Service.org_uuid == org_uuid).filter(
                Service.service_id == service_id).first()
            service = ServiceFactory().convert_service_db_model_to_entity_model(service_db)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return org_uuid, service

    def save_service_comments(self, service_comment):
        self.add_item(
            ServiceComment(
                org_uuid=service_comment.org_uuid,
                service_uuid=service_comment.service_uuid,
                support_type=service_comment.support_type,
                user_type=service_comment.user_type,
                commented_by=service_comment.commented_by,
                comment=service_comment.comment,
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()

            )
        )
        return service_comment.to_dict()

    def get_last_service_comment(self, org_uuid, service_uuid, support_type, user_type):
        try:
            service_comment_db = self.session.query(ServiceComment) \
                .filter(ServiceComment.org_uuid == org_uuid). \
                filter(ServiceComment.service_uuid == service_uuid). \
                filter(ServiceComment.support_type == support_type). \
                filter(ServiceComment.user_type == user_type). \
                order_by(ServiceComment.created_on.desc()).first()
            service_comment = ServiceFactory().convert_service_comment_db_model_to_entity_model(service_comment_db)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return service_comment

    def get_list_of_service_pending_for_approval(self, limit):
        try:
            raw_services_data = self.session.query(Service) \
                .join(ServiceState, Service.uuid == ServiceState.service_uuid).filter(
                ServiceState.state == ServiceStatus.APPROVAL_PENDING.value).limit(limit)
            services = []
            for service in raw_services_data:
                services.append(ServiceFactory().convert_service_db_model_to_entity_model(service))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return services

    def get_service_state_with_status(self, status):
        service_state_db = self.session.query(ServiceState).filter(ServiceState.state == status).all()
        service_state = ServiceFactory.convert_service_state_from_db_list(service_state_db)
        self.session.commit()
        return service_state

    def update_service_status(self, service_uuid_list, prev_state, next_state):
        self.session.query(ServiceState).filter(ServiceState.service_uuid.in_(service_uuid_list)) \
            .filter(ServiceState.state == prev_state).update({ServiceState.state: next_state},
                                                             synchronize_session=False)
        self.session.commit()

    def update_service(self, org_uuid, service_uuid, assets=None):
        try:
            service = self.session.query(Service).filter(org_uuid == org_uuid) \
                .filter(service_uuid == service_uuid).first()
            if service:
                if assets:
                    service.assets = assets
                self.session.commit()
            else:
                raise Exception(f"Service {service_uuid} not found for org {org_uuid}")
        except SQLAlchemyError as error:
            self.session.rollback()
            raise error
        except Exception as e:
            raise e
