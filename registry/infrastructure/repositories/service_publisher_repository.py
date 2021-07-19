from datetime import datetime as dt

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from registry.constants import ServiceStatus
from registry.domain.factory.service_factory import ServiceFactory
from registry.infrastructure.models import Service, ServiceGroup, ServiceState, ServiceReviewHistory, Organization, \
    ServiceComment, OffchainServiceConfig
from registry.infrastructure.repositories.base_repository import BaseRepository
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

org_repo = OrganizationPublisherRepository()


class ServicePublisherRepository(BaseRepository):
    def get_services_for_organization(self, org_uuid, payload):
        try:
            services_db = self.session.query(Service). \
                filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
                filter(Service.org_uuid == org_uuid). \
                order_by(getattr(getattr(Service, payload["sort_by"]), payload["order_by"])()). \
                slice(payload["offset"], payload["limit"]).all()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        services = []
        for service in services_db:
            services.append(ServiceFactory().convert_service_db_model_to_entity_model(service))
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
            service_db = self.session.query(Service).filter(Service.org_uuid == service.org_uuid).filter(
                Service.uuid == service.uuid).first()
            service_db.display_name = service.display_name
            service_db.service_id = service.service_id
            service_db.metadata_uri = service.metadata_uri
            service_db.proto = service.proto
            service_db.short_description = service.short_description
            service_db.description = service.description
            service_db.project_url = service.project_url
            service_db.assets = service.assets
            service_db.rating = service.rating
            service_db.ranking = service.ranking
            service_db.contributors = service.contributors
            service_db.tags = service.tags
            service_db.mpe_address = service.mpe_address
            service_db.updated_on = dt.utcnow()
            service_db.groups = service_group_db_model
            service_db.service_state.state = state
            service_db.service_state.transaction_hash = service.service_state.transaction_hash
            service_db.service_state.updated_by = username
            service_db.service_state.updated_on = dt.utcnow()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        if not service_db:
            return None
        service = ServiceFactory().convert_service_db_model_to_entity_model(service_db)
        return service

    def get_service_for_given_service_uuid(self, org_uuid, service_uuid):
        try:
            service_db = self.session.query(Service).filter(Service.org_uuid == org_uuid).filter(
                Service.uuid == service_uuid).first()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        if not service_db:
            return None
        service = ServiceFactory().convert_service_db_model_to_entity_model(service_db)
        return service

    def get_service_for_given_service_id_and_org_id(self, org_id, service_id):
        try:
            service_db = self.session.query(Service). \
                join(Organization, Service.org_uuid == Organization.uuid). \
                filter(Organization.org_id == org_id). \
                filter(Service.service_id == service_id). \
                first()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        if service_db:
            service = ServiceFactory().convert_service_db_model_to_entity_model(service_db)
            return service.org_uuid, service
        organization = org_repo.get_organization(org_id=org_id)
        if organization:
            return organization.uuid, None
        raise Exception(f"No organization found for org_id:{org_id} service_id:{service_id}")

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

    def get_last_service_comment(self, org_uuid, service_uuid, support_type, user_type):
        try:
            service_comment_db = self.session.query(ServiceComment) \
                .filter(ServiceComment.org_uuid == org_uuid). \
                filter(ServiceComment.service_uuid == service_uuid). \
                filter(ServiceComment.support_type == support_type). \
                filter(ServiceComment.user_type == user_type). \
                order_by(ServiceComment.created_on.desc()).first()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        if not service_comment_db:
            return None
        service_comment = ServiceFactory().convert_service_comment_db_model_to_entity_model(service_comment_db)
        return service_comment

    def get_service_state(self, status):
        try:
            services_state_db = self.session.query(ServiceState).filter(ServiceState.state == status).all()
            self.session.commit()
        except SQLAlchemyError as error:
            self.session.rollback()
            raise error
        services_state = []
        for service_state_db in services_state_db:
            service_state = ServiceFactory.convert_service_state_from_db(service_state_db)
            services_state.append(service_state)
        return services_state

    def update_service_status(self, service_uuid_list, prev_state, next_state):
        try:
            self.session.query(ServiceState).filter(ServiceState.service_uuid.in_(service_uuid_list)) \
                .filter(ServiceState.state == prev_state).update({ServiceState.state: next_state},
                                                                 synchronize_session=False)
            self.session.commit()
        except SQLAlchemyError as error:
            self.session.rollback()
            raise error

    def get_offchain_service_config(self, org_uuid, service_uuid):
        try:
            offchain_service_config_db = self.session.query(OffchainServiceConfig).\
                filter(OffchainServiceConfig.org_uuid == org_uuid).\
                filter(OffchainServiceConfig.service_uuid == service_uuid).\
                all()
            self.session.commit()
        except SQLAlchemyError as error:
            self.session.rollback()
            raise error
        offchain_service_config = ServiceFactory().convert_offchain_service_config_db_model_to_entity_model(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            offchain_service_configs_db=offchain_service_config_db
        )
        return offchain_service_config
