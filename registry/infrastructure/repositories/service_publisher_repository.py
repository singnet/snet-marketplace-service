from typing import List

import sqlalchemy
from sqlalchemy import func

from registry.domain.factory.service_factory import ServiceFactory
from registry.infrastructure.models import (
    Service,
    ServiceGroup,
    ServiceState,
    Organization,
    ServiceComment,
    OffchainServiceConfig
)
from registry.exceptions import ServiceNotFoundException
from registry.infrastructure.repositories.base_repository import BaseRepository
from registry.domain.models.service import Service as ServiceEntity
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from common.logger import get_logger


org_repo = OrganizationPublisherRepository()
logger = get_logger(__name__)


class ServicePublisherRepository(BaseRepository):
    def get_services_for_organization(self, org_uuid, payload) -> List[ServiceEntity]:
        services_db = self.session.query(Service). \
            filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
            filter(Service.org_uuid == org_uuid). \
            order_by(getattr(getattr(Service, payload["sort_by"]), payload["order_by"])()). \
            offset(payload["offset"]).limit(payload["limit"]).all()

        return [ServiceFactory.convert_service_db_model_to_entity_model(service_db) for service_db in services_db]

    def get_total_count_of_services_for_organization(self, org_uuid, payload):
        total_count_of_services = self.session.query(func.count(Service.uuid)). \
            filter(getattr(Service, payload["search_attribute"]).like("%" + payload["search_string"] + "%")). \
            filter(Service.org_uuid == org_uuid).all()[0][0]
    
        return total_count_of_services

    def check_service_id_within_organization(self, org_uuid, service_id):
        record_exist = self.session.query(func.count(Service.uuid)) \
            .filter(Service.org_uuid == org_uuid) \
            .filter(Service.service_id == service_id).all()[0][0]

        return record_exist

    def add_service(self, service, username):
        service_db_model = ServiceFactory().convert_service_entity_model_to_db_model(username, service)
        self.add_item(service_db_model)

    @BaseRepository.write_ops
    def save_service(self, username, service, state):
        service_group_db_model = [
            ServiceFactory().convert_service_group_entity_model_to_db_model(group) for group in service.groups
        ]
        try:
            self.session.query(ServiceGroup).filter(ServiceGroup.org_uuid == service.org_uuid).filter(
                ServiceGroup.service_uuid == service.uuid).delete(synchronize_session='fetch')
        #     self.session.commit()
        # except Exception as e:
        #     self.session.rollback()
        #     raise e
        #
        # try:
            service_db = self.session.query(Service) \
                .filter(Service.org_uuid == service.org_uuid) \
                .filter(Service.uuid == service.uuid).first()
           
            if service_db is None:
                raise ServiceNotFoundException

            logger.info(f"state service_uuid: {service_db.service_state.service_uuid}, db state: {service_db.service_state.state}, new state: {state}")
            logger.info(f"groups: {service_db.groups}")
            try:
                logger.info(f"group service_uuid: {service_db.groups[0].service_uuid}")
            except Exception as e:
                logger.info(f"error: {e}")

            service_db.display_name = service.display_name
            service_db.service_id = service.service_id
            service_db.metadata_uri = service.metadata_uri
            if service.storage_provider:
                service_db.storage_provider = service.storage_provider
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
            service_db.groups = service_group_db_model
            service_db.service_state.state = state
            service_db.service_type = service.service_type
            service_db.service_state.transaction_hash = service.service_state.transaction_hash
            service_db.service_state.updated_by = username
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return ServiceFactory().convert_service_db_model_to_entity_model(service_db) if service_db else None

    def get_service_for_given_service_uuid(self, org_uuid, service_uuid):
        service_db = self.session.query(Service) \
            .filter(Service.org_uuid == org_uuid) \
            .filter(Service.uuid == service_uuid).first()

        return ServiceFactory().convert_service_db_model_to_entity_model(service_db) if service_db else None

    def get_service_for_given_service_id_and_org_id(
            self,
            org_id: str,
            service_id: str
        ) -> ServiceEntity | None:
        service_db = self.session.query(Service). \
            join(Organization, Service.org_uuid == Organization.uuid). \
            filter(Organization.org_id == org_id). \
            filter(Service.service_id == service_id). \
            first()
    
        if service_db is None:
            raise ServiceNotFoundException()

        return ServiceFactory().convert_service_db_model_to_entity_model(service_db)

    def save_service_comments(self, service_comment):
        self.add_item(
            ServiceComment(
                org_uuid=service_comment.org_uuid,
                service_uuid=service_comment.service_uuid,
                support_type=service_comment.support_type,
                user_type=service_comment.user_type,
                commented_by=service_comment.commented_by,
                comment=service_comment.comment,
            )
        )

    def get_last_service_comment(
            self,
            org_uuid: str,
            service_uuid: str,
            support_type: str,
            user_type
        ):
        service_comment_db = self.session.query(ServiceComment) \
            .filter(ServiceComment.org_uuid == org_uuid) \
            .filter(ServiceComment.service_uuid == service_uuid) \
            .filter(ServiceComment.support_type == support_type) \
            .filter(ServiceComment.user_type == user_type) \
            .order_by(ServiceComment.created_on.desc()).first()
        
        return ServiceFactory().convert_service_comment_db_model_to_entity_model(service_comment_db) if service_comment_db else None

    def get_service_state(self, status):
        services_states_db = self.session.query(ServiceState). \
            filter(ServiceState.state == status).all()
            
        return [ServiceFactory.convert_service_state_from_db(service_state_db) for service_state_db in services_states_db]

    @BaseRepository.write_ops
    def update_service_status(self, service_uuid_list, prev_state, next_state):
        self.session.query(ServiceState).filter(ServiceState.service_uuid.in_(service_uuid_list)) \
            .filter(ServiceState.state == prev_state) \
            .update(
                {ServiceState.state: next_state},
                synchronize_session=False
            )
        self.session.commit()

    def get_offchain_service_config(self, org_uuid, service_uuid):
        sql_query = sqlalchemy.text(f"select * from offchain_service_config where service_uuid = '{service_uuid}' and org_uuid = '{org_uuid}'")
        result = self.session.execute(sql_query)
        result_as_list = result.fetchall()
        logger.info(f"offchain configs :: {result_as_list}")
        offchain_service_config = ServiceFactory().convert_offchain_service_config_db_model_to_entity_model(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            offchain_service_configs_db=result_as_list
        )
        return offchain_service_config

    @BaseRepository.write_ops
    def add_or_update_offline_service_config(self, offchain_service_config):
        configs = offchain_service_config.configs
        for key in configs:
            parameter_name = key
            parameter_value = configs[key]
            offchain_service_config_db = self.session.query(OffchainServiceConfig). \
                filter(OffchainServiceConfig.org_uuid == offchain_service_config.org_uuid). \
                filter(OffchainServiceConfig.service_uuid == offchain_service_config.service_uuid). \
                filter(OffchainServiceConfig.parameter_name == parameter_name). \
                first()

            if offchain_service_config_db:
                offchain_service_config_db.parameter_value = parameter_value
            self.session.commit()

            if not offchain_service_config_db:
                self.add_item(OffchainServiceConfig(
                    org_uuid=offchain_service_config.org_uuid,
                    service_uuid=offchain_service_config.service_uuid,
                    parameter_name=parameter_name,
                    parameter_value=parameter_value,
                ))