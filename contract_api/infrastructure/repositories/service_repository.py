from collections import defaultdict
from datetime import datetime as dt
import json
from typing import List

from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.orm import Query
from sqlalchemy.sql import Subquery

from contract_api.domain.models.offchain_service_attribute import OffchainServiceAttributeEntityModel
from contract_api.infrastructure.models import (Organization,
                                                Service,
                                                ServiceEndpoint,
                                                ServiceMedia,
                                                ServiceMetadata,
                                                ServiceTags,
                                                ServiceGroup)
from contract_api.infrastructure.models import OffchainServiceConfig
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.domain.models.service import ServiceEntityModel
from contract_api.application.schema.service import (FilterCondition,
                                                     GetServiceRequest,
                                                     OrderEnum,
                                                     AttributeNameEnum,
                                                     Sort,
                                                     operator_mapping,
                                                     column_mapping)

service_factory = ServiceFactory()


class ServiceRepository(BaseRepository):

    def get_service(self, org_id: str, service_id: str) -> ServiceEntityModel:
        service_db = self.session.query(Service). \
            filter(Service.org_id == org_id). \
            filter(Service.service_id == service_id).first()
        return service_factory.convert_service_db_model_to_entity_model(service_db) \
            if service_db else None

    def get_services_by_attribute_name(self, attribute_name: AttributeNameEnum):

        # Build the query based on the attribute
        if attribute_name == AttributeNameEnum.TAG_NAME:
            query = (
                select(ServiceTags.tag_name.label("key"), ServiceTags.tag_name.label("key"))
                .distinct()
                .select_from(ServiceTags)
                .join(Service, Service.row_id == ServiceTags.service_row_id)
                .where(Service.is_curated == 1)
            )
        elif attribute_name == AttributeNameEnum.DISPLAY_NAME:
            query = (
                select(Service.service_id.label("key"), ServiceMetadata.display_name.label("value"))
                .distinct()
                .select_from(ServiceMetadata)
                .join(Service, Service.row_id == ServiceMetadata.service_row_id)
                .where(Service.is_curated == 1)
            )
        elif attribute_name == AttributeNameEnum.ORG_ID:
            query = (
                select(Organization.org_id.label("key"), Organization.organization_name.label("value"))
                .distinct()
                .select_from(Organization)
                .join(Service, Service.org_id == Organization.org_id)
                .where(Service.is_curated == 1)
            )
        else:
            return []
    
        return self.session.execute(query).all()

    def __apply_filters(self, db_model, query: Query, filters: List[FilterCondition]) -> Query:
        for filter_cond in filters:
            column = getattr(db_model, filter_cond.attribute, None)
            if column is not None:
                operation = operator_mapping.get(filter_cond.operator)
                if operation:
                    query = query.filter(operation(column, filter_cond.value))

        return query

    def __map_sorting(self, sort_params: Sort) -> Subquery:
        if sort_params is None:
            return asc(Service.service_id)
        elif sort_params.order == OrderEnum.DESC:
            return desc(column_mapping[sort_params.by])
        elif sort_params.order == OrderEnum.ASC:
            return asc(column_mapping[sort_params.by])

    def __make_subquery_service_metadata(self):
        subquery = (
            select(
                ServiceMetadata.org_id,
                ServiceMetadata.service_id,
                ServiceEndpoint.is_available,
                func.group_concat(ServiceTags.tag_name).label("tags"),
            )
            .outerjoin(ServiceTags, ServiceMetadata.service_row_id == ServiceTags.service_row_id)
            .outerjoin(ServiceEndpoint, ServiceMetadata.service_row_id == ServiceEndpoint.service_row_id)
            .group_by(ServiceMetadata.org_id, ServiceMetadata.service_id, ServiceEndpoint.is_available)
            .subquery()
        )
        return subquery

    def get_services(self, params: GetServiceRequest):
        additional_order_by = self.__map_sorting(sort_params=params.sort)

        # Step 1: Create the subquery for service metadata
        subquery = self.__make_subquery_service_metadata()

        # Step 2: Main query to fetch services with organization details
        query = (
            self.session.query(
                Service,
                ServiceMetadata,
                Organization,
                ServiceMedia,
                subquery.c.is_available,
                subquery.c.tags,
            )
            .join(ServiceMetadata)
            .join(Organization, Service.org_id == Organization.org_id)
            .join(subquery, and_(Service.org_id == subquery.c.org_id, Service.service_id == subquery.c.service_id))
            .join(ServiceMedia, and_(Service.org_id == ServiceMedia.org_id,
                                     Service.service_id == ServiceMedia.service_id,
                                     ServiceMedia.order == 1))
        )

        # Step 3: Apply search filter if provided
        if params.search is not None:
            search_query = f"%{params.search}%"
            query = query.filter(Service.service_id.like(search_query))

        # Step 4: Apply filters
        query = self.__apply_filters(db_model=Service, query=query, filters=params.filters)

        # Step 5: Order, limit, and offset the results
        query = query.order_by(
            desc(subquery.c.is_available),
            additional_order_by
        ).limit(params.limit).offset(params.offset)

        # Execute the query to fetch services
        services_db = query.all()

        # Step 6: Fetch the total count of services
        total_count = self.session.query(func.count(Service.row_id)).scalar()

        services = [ServiceFactory.create_service_full_info_entity_model(
            service_db=service_db.Service,
            service_metadata_db=service_db.ServiceMetadata,
            organization_db=service_db.Organization,
            service_media_db=service_db.ServiceMedia,
            tags=service_db.tags.split(",") if service_db.tags else [],
            is_available=service_db.is_available
        ) for service_db in services_db]

        return services, total_count

    def get_service_group_data(self, org_id: int, service_id: int):
        group_data = (
            self.repo.query(ServiceGroup, ServiceEndpoint)
            .join(ServiceEndpoint, ServiceGroup.group_id == ServiceEndpoint.group_id)
            .filter(ServiceGroup.org_id == org_id, ServiceGroup.service_id == service_id)
            .all()
        )

        # Initialize the groups dictionary
        groups = defaultdict(lambda: {
            "group_id": None,
            "group_name": "",
            "pricing": {},
            "endpoints": [],
            "free_calls": 0,
            "free_call_signer_address": ""
        })

        # Process the query results
        for group in group_data:
            group_id = group.group_id

            if groups[group_id]["group_id"] is None:
                # Initialize group info
                groups[group_id]["group_id"] = group.group_id
                groups[group_id]["group_name"] = group.group_name
                groups[group_id]["pricing"] = json.loads(group.pricing)
                groups[group_id]["free_calls"] = group.free_calls or 0
                groups[group_id]["free_call_signer_address"] = group.free_call_signer_address or ""

            # Append endpoint info
            groups[group_id]["endpoints"].append({
                "endpoint": group.service_endpoint.endpoint,
                "is_available": group.service_endpoint.is_available,
                "last_check_timestamp": group.service_endpoint.last_check_timestamp
            })

        return list(groups.values())


    def get_service_full_data(self, org_id: int, service_id: int):

        subquery = self.__make_subquery_service_metadata()

        query = (
            self.session.query(
                Service,
                ServiceMetadata,
                Organization,
                ServiceMedia,
                subquery.c.is_available,
                subquery.c.tags,
            )
            .join(ServiceMetadata)
            .join(Organization, Service.org_id == Organization.org_id)
            .join(subquery, and_(Service.org_id == subquery.c.org_id, Service.service_id == subquery.c.service_id))
            .join(ServiceMedia, and_(Service.org_id == ServiceMedia.org_id,
                                     Service.service_id == ServiceMedia.service_id,
                                     ServiceMedia.order == 1))
            .filter(Service.org_id == org_id, Service.service_id == service_id)
        )

        service_db = self.session.execute(query).fetchone()

        return ServiceFactory.create_service_full_info_entity_model(
            service_db=service_db.Service,
            service_metadata_db=service_db.ServiceMetadata,
            organization_db=service_db.Organization,
            service_media_db=service_db.ServiceMedia,
            tags=service_db.tags.split(",") if service_db.tags else [],
            is_available=service_db.is_available
        )


class OffchainServiceConfigRepository(BaseRepository):

    def get_offchain_service_config(self, org_id, service_id) -> OffchainServiceAttributeEntityModel:
        offchain_service_configs_db = self.session.query(OffchainServiceConfig). \
            filter(OffchainServiceConfig.org_id == org_id). \
            filter(OffchainServiceConfig.service_id == service_id). \
            all()
        offchain_service_config = ServiceFactory().convert_offchain_service_configs_db_model_to_entity_model(
            org_id=org_id,
            service_id=service_id,
            offchain_service_configs_db=offchain_service_configs_db
        )

        return offchain_service_config

    @BaseRepository.write_ops
    def save_offchain_service_attribute(self, offchain_service_attribute):
        attributes = offchain_service_attribute.attributes
        for key in attributes:
            parameter_name = key
            parameter_value = attributes[key]
            offchain_service_config_db = self.session.query(OffchainServiceConfig). \
                filter(OffchainServiceConfig.org_id == offchain_service_attribute.org_id). \
                filter(OffchainServiceConfig.service_id == offchain_service_attribute.service_id). \
                filter(OffchainServiceConfig.parameter_name == parameter_name). \
                first()
            if offchain_service_config_db:
                offchain_service_config_db.parameter_value = parameter_value
                offchain_service_config_db.updated_on=dt.utcnow()
            else:
                self.add_item(OffchainServiceConfig(
                    org_id=offchain_service_attribute.org_id,
                    service_id=offchain_service_attribute.service_id,
                    parameter_name=parameter_name,
                    parameter_value=parameter_value,
                    created_on=dt.utcnow(),
                    updated_on=dt.utcnow()
                ))
        self.session.commit()

        return offchain_service_attribute
