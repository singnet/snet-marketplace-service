import datetime as dt

from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.exc import SQLAlchemyError

from contract_api.domain.factory.organization_factory import OrganizationFactory
from contract_api.domain.models.offchain_service_attribute import OffchainServiceConfigDomain
from contract_api.domain.models.organization import OrganizationDomain
from contract_api.domain.models.service import ServiceDomain
from contract_api.domain.models.service_endpoint import ServiceEndpointDomain
from contract_api.domain.models.service_group import ServiceGroupDomain
from contract_api.domain.models.service_media import ServiceMediaDomain
from contract_api.domain.models.service_metadata import ServiceMetadataDomain
from contract_api.domain.models.service_tag import ServiceTagDomain
from contract_api.infrastructure.models import Service as ServiceDB, ServiceMetadata as ServiceMetadataDB, \
    ServiceEndpoint, ServiceTags, Service, ServiceMetadata, Organization, ServiceMedia, ServiceGroup
from contract_api.infrastructure.models import OffchainServiceConfig
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from contract_api.domain.factory.service_factory import ServiceFactory
from contract_api.constant import SortKeys, SortOrder, FilterKeys



class ServiceRepository(BaseRepository):

    def get_service_endpoint(self, org_id: str, service_id: str, group_id: str) -> str:
        query = select(
            ServiceEndpoint.endpoint
        ).where(
            ServiceEndpoint.org_id == org_id,
            ServiceEndpoint.service_id == service_id,
            ServiceEndpoint.group_id == group_id
        ).limit(1)

        result = self.session.execute(query)
        return result.scalar()

    def get_unique_service_tags(self) -> list[ServiceTagDomain]:
        query = select(
            ServiceTags
        ).join(
            Service, ServiceTags.service_row_id == Service.row_id
        ).where(
            Service.is_curated == True
        ).distinct(ServiceTags.tag_name)

        result = self.session.execute(query)
        tags_db = result.scalars().all()

        return ServiceFactory.service_tags_from_db_model(tags_db)

    def get_filtered_services(
            self,
            limit: int,
            page: int,
            sort: str,
            order: str,
            filters: dict,
            q: str
    ) -> list[dict]:
        query = select(
            Service.org_id.label("orgId"),
            Organization.organization_name.label("organizationName"),
            Service.service_id.label("serviceId"),
            ServiceMetadata.display_name.label("displayName"),
            ServiceMetadata.service_rating["rating"].label("rating"),
            ServiceMetadata.service_rating["total_users_rated"].label("numberOfRatings"),
            ServiceMetadata.short_description.label("shortDescription"),
            func.max(ServiceEndpoint.is_available).label("isAvailable"),
            Organization.org_assets_url["hero_image"].label("orgImageUrl"),
            ServiceMedia.url.label("serviceImageUrl")
        ).join(
            ServiceMetadata, ServiceMetadata.service_row_id == Service.row_id
        ).join(
            Organization, Organization.org_id == Service.org_id
        ).join(
            ServiceEndpoint, ServiceEndpoint.service_row_id == Service.row_id, isouter = True
        ).join(
            ServiceMedia, and_(
                ServiceMedia.service_row_id == Service.row_id,
                ServiceMedia.asset_type == "hero_image"
            ),
            isouter = True
        ).where(
            Service.is_curated == True
        ).group_by(
            Service.org_id,
            Organization.organization_name,
            Service.service_id,
            ServiceMetadata.display_name,
            ServiceMetadata.service_rating["rating"],
            ServiceMetadata.service_rating["total_users_rated"],
            ServiceMetadata.short_description,
            ServiceEndpoint.is_available,
            Organization.org_assets_url["hero_image"],
            ServiceMedia.url
        )

        if filters:
            query_filters = []

            if FilterKeys.ORG_ID in filters and filters[FilterKeys.ORG_ID]:
                query_filters.append(Service.org_id.in_(filters[FilterKeys.ORG_ID]))

            if FilterKeys.TAG_NAME in filters and filters[FilterKeys.TAG_NAME]:
                tag_subquery = select(
                    ServiceTags.service_row_id
                ).where(
                    ServiceTags.tag_name.in_(filters[FilterKeys.TAG_NAME])
                ).subquery()
                query_filters.append(Service.row_id.in_(tag_subquery))

            if FilterKeys.ONLY_AVAILABLE in filters and filters[FilterKeys.ONLY_AVAILABLE]:
                query_filters.append(ServiceEndpoint.is_available == True)

            if query_filters:
                query = query.where(and_(*query_filters))

        if q:
            search = f"%{q}%"
            query = query.where(
                or_(
                    ServiceMetadata.display_name.ilike(search),
                    ServiceMetadata.short_description.ilike(search)
                )
            )

        sort_mapping = {
            SortKeys.DISPLAY_NAME.value: ServiceMetadata.display_name,
            SortKeys.RANKING.value: ServiceMetadata.ranking,
            SortKeys.RATING.value: ServiceMetadata.service_rating["rating"].as_integer(),
            SortKeys.NUMBER_OF_RATINGS.value: ServiceMetadata.service_rating["total_users_rated"].as_integer()
        }

        if sort in sort_mapping:
            sort_column = sort_mapping[sort]
            if order == SortOrder.DESC:
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

        query = query.limit(limit).offset((page - 1) * limit)

        result = self.session.execute(query)

        return result.mappings().all()

    def get_filtered_services_count(
            self,
            filters: dict,
            q: str
    ) -> int:
        subquery = select(
            Service.row_id
        ).join(
            ServiceMetadata, ServiceMetadata.service_row_id == Service.row_id
        ).join(
            Organization, Organization.org_id == Service.org_id
        ).join(
            ServiceEndpoint, ServiceEndpoint.service_row_id == Service.row_id, isouter = True
        ).where(
            Service.is_curated == True
        )

        if filters:
            query_filters = []

            if FilterKeys.ORG_ID in filters and filters[FilterKeys.ORG_ID]:
                query_filters.append(Service.org_id.in_(filters[FilterKeys.ORG_ID]))

            if FilterKeys.TAG_NAME in filters and filters[FilterKeys.TAG_NAME]:
                tag_subquery = select(
                    ServiceTags.service_row_id
                ).where(
                    ServiceTags.tag_name.in_(filters[FilterKeys.TAG_NAME])
                ).subquery()
                query_filters.append(Service.row_id.in_(tag_subquery))

            if FilterKeys.ONLY_AVAILABLE in filters and filters[FilterKeys.ONLY_AVAILABLE]:
                query_filters.append(ServiceEndpoint.is_available == True)

            if query_filters:
                subquery = subquery.where(and_(*query_filters))

        if q:
            search = f"%{q}%"
            subquery = subquery.where(
                or_(
                    ServiceMetadata.display_name.ilike(search),
                    ServiceMetadata.short_description.ilike(search)
                )
            )

        count_query = select(func.count()).select_from(subquery.subquery())

        result = self.session.execute(count_query)
        return result.scalar()

    def get_service(
            self, org_id: str, service_id: str
    ) -> tuple[ServiceDomain, OrganizationDomain, ServiceMetadataDomain]:
        query = select(
            Service,
            Organization,
            ServiceMetadata,
        ).join(
            Organization, Organization.org_id == Service.org_id
        ).join(
            ServiceMetadata, ServiceMetadata.service_row_id == Service.row_id
        ).where(
            Service.org_id == org_id,
            Service.service_id == service_id,
            Service.is_curated == True
        ).limit(1)

        result = self.session.execute(query)
        service, organization, service_metadata = result.scalar_one_or_none()
        return (
            ServiceFactory.service_from_db_model(service),
            OrganizationFactory.organization_from_db_model(organization),
            ServiceFactory.service_metadata_from_db_model(service_metadata)
        )

    def get_service_media(self, org_id: str, service_id: str) -> list[ServiceMediaDomain]:
        query = select(
            ServiceMedia
        ).where(
            ServiceMedia.org_id == org_id,
            ServiceMedia.service_id == service_id
        )

        result = self.session.execute(query)
        service_media_db = result.scalars().all()

        return ServiceFactory.service_media_from_db_model(service_media_db)

    def get_service_groups(
            self, org_id: str, service_id: str
    ) -> list[tuple[ServiceGroupDomain, ServiceEndpointDomain]]:
        query = select(
            ServiceGroup,
            ServiceEndpoint
        ).join(
            ServiceEndpoint, and_(
                ServiceEndpoint.service_row_id == ServiceGroup.service_id,
                ServiceEndpoint.group_id == ServiceGroup.group_id
            )
        ).where(
            ServiceGroup.org_id == org_id,
            ServiceGroup.service_id == service_id
        )

        result = self.session.execute(query)
        groups_endpoints_db = result.scalars().all()

        return [
            (
                ServiceFactory.service_group_from_db_model(group_endpoint_db[0]),
                ServiceFactory.service_endpoint_from_db_model(group_endpoint_db[1])
            )
            for group_endpoint_db in groups_endpoints_db
        ]

    def get_service_tags(
            self, org_id: str, service_id: str
    ) -> list[ServiceTagDomain]:
        query = select(
            ServiceTags
        ).where(
            ServiceTags.org_id == org_id,
            ServiceTags.service_id == service_id
        )

        result = self.session.execute(query)
        service_tags_db = result.scalars().all()

        return ServiceFactory.service_tags_from_db_model(service_tags_db)

    def get_offchain_service_configs(
            self, org_id: str, service_id: str
    ) -> list[OffchainServiceConfigDomain]:
        query = select(
            OffchainServiceConfig
        ).where(
            OffchainServiceConfig.org_id == org_id,
            OffchainServiceConfig.service_id == service_id
        )

        result = self.session.execute(query)
        offchain_service_config_db = result.scalars().all()

        return ServiceFactory.offchain_service_configs_from_db_model_list(offchain_service_config_db)

    def curate_service(self, org_id, service_id, curate):
        query = update(
            Service
        ).where(
            Service.org_id == org_id,
            Service.service_id == service_id
        ).values(
            is_curated=curate
        )

        self.session.execute(query)
        self.session.commit()

    def upsert_offchain_service_config(
            self,
            org_id: str,
            service_id: str,
            offchain_service_configs: list[OffchainServiceConfigDomain]) -> None:
        for offchain_service_config in offchain_service_configs:
            query = select(
                OffchainServiceConfig
            ).where(
                OffchainServiceConfig.org_id == org_id,
                OffchainServiceConfig.service_id == service_id,
                OffchainServiceConfig.parameter_name == offchain_service_config.parameter_name
            ).limit(1)

            result = self.session.execute(query)
            offchain_service_config_db = result.scalar_one_or_none()

            if offchain_service_config_db:
                query = update(
                    OffchainServiceConfig
                ).where(
                    OffchainServiceConfig.org_id == org_id,
                    OffchainServiceConfig.service_id == service_id,
                    OffchainServiceConfig.parameter_name == offchain_service_config.parameter_name
                ).values(
                    parameter_value=offchain_service_config.parameter_value
                )

                self.session.execute(query)
            else:
                self.session.add(OffchainServiceConfig(
                    org_id=org_id,
                    service_id=service_id,
                    parameter_name=offchain_service_config.parameter_name,
                    parameter_value=offchain_service_config.parameter_value
                ))
            self.session.commit()

    def get_service(self, org_id, service_id):
        try:
            service_db = self.session.query(ServiceDB). \
                filter(ServiceDB.org_id == org_id). \
                filter(ServiceDB.service_id == service_id). \
                first()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not service_db:
            return None
        return service_factory.convert_service_db_model_to_entity_model(service_db)

    def create_or_update_service(self, service):
        current_datetime = dt.datetime.now(dt.UTC)
        try:
            service_db = self.session.query(ServiceDB). \
                filter(ServiceDB.org_id == service.org_id). \
                filter(ServiceDB.service_id == service.service_id). \
                first()
            if service_db:
                service_db.hash_uri = service.hash_uri,
                service_db.is_curated = service.is_curated,
                service_db.service_email = service.service_email
                service_db.row_updated = current_datetime
                service_db.service_metadata.display_name = service.service_metadata.display_name
                service_db.service_metadata.description = service.service_metadata.description
                service_db.service_metadata.short_description = service.service_metadata.short_description
                service_db.service_metadata.url = service.service_metadata.url
                service_db.service_metadata.json = service.service_metadata.json
                service_db.service_metadata.model_hash = service.service_metadata.model_hash
                service_db.service_metadata.encoding = service.service_metadata.encoding
                service_db.service_metadata.type = service.service_metadata.type
                service_db.service_metadata.mpe_address = service.service_metadata.mpe_address
                service_db.service_metadata.assets_url = service.service_metadata.assets_url
                service_db.service_metadata.assets_hash = service.service_metadata.assets_hash
                service_db.service_metadata.service_rating = service.service_metadata.service_rating
                service_db.service_metadata.ranking = service.service_metadata.ranking
                service_db.service_metadata.demo_component_available = service.service_metadata.demo_component_available
                service_db.service_metadata.contributors = service.service_metadata.contributors
                service_db.service_metadata.row_updated = current_datetime
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        if not service_db:
            self.add_item(ServiceDB(
                org_id=service.org_id,
                service_id=service.service_id,
                service_path=None,
                hash_uri=service.hash_uri,
                is_curated=service.is_curated,
                service_email=service.service_email,
                row_created=current_datetime,
                row_updated=current_datetime,
                service_metadata=ServiceMetadataDB(
                    org_id=service.service_metadata.org_id,
                    service_id=service.service_metadata.service_id,
                    display_name=service.service_metadata.display_name,
                    description=service.service_metadata.description,
                    short_description=service.service_metadata.short_description,
                    demo_component_available=service.service_metadata.demo_component_available,
                    url=service.service_metadata.url,
                    json=service.service_metadata.json,
                    model_hash=service.service_metadata.model_hash,
                    encoding=service.service_metadata.encoding,
                    type=service.service_metadata.type,
                    mpe_address=service.service_metadata.mpe_address,
                    assets_url=service.service_metadata.assets_url,
                    assets_hash=service.service_metadata.assets_hash,
                    service_rating=service.service_metadata.service_rating,
                    ranking=service.service_metadata.ranking,
                    contributors=service.service_metadata.contributors,
                    row_created=current_datetime,
                    row_updated=current_datetime
                )
            ))


class OffchainServiceConfigRepository(BaseRepository):
    pass

    def get_offchain_service_config(self, org_id, service_id):
        try:
            offchain_service_configs_db = self.session.query(OffchainServiceConfig). \
                filter(OffchainServiceConfig.org_id == org_id). \
                filter(OffchainServiceConfig.service_id == service_id). \
                all()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        offchain_service_config = ServiceFactory().convert_offchain_service_configs_db_model_to_entity_model(
            org_id=org_id,
            service_id=service_id,
            offchain_service_configs_db=offchain_service_configs_db
        )
        return offchain_service_config

    def save_offchain_service_attribute(self, offchain_service_attribute):
        attributes = offchain_service_attribute.attributes
        current_datetime = dt.datetime.now(dt.UTC)
        for key in attributes:
            parameter_name = key
            parameter_value = attributes[key]
            try:
                offchain_service_config_db = self.session.query(OffchainServiceConfig). \
                    filter(OffchainServiceConfig.org_id == offchain_service_attribute.org_id). \
                    filter(OffchainServiceConfig.service_id == offchain_service_attribute.service_id). \
                    filter(OffchainServiceConfig.parameter_name == parameter_name). \
                    first()
                if offchain_service_config_db:
                    offchain_service_config_db.parameter_value = parameter_value
                    offchain_service_config_db.updated_on=current_datetime
                self.session.commit()
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e
            if not offchain_service_config_db:
                self.add_item(OffchainServiceConfig(
                    org_id=offchain_service_attribute.org_id,
                    service_id=offchain_service_attribute.service_id,
                    parameter_name=parameter_name,
                    parameter_value=parameter_value,
                    created_on=current_datetime,
                    updated_on=current_datetime
                ))
        return offchain_service_attribute
