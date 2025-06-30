import datetime as dt

from sqlalchemy import select, and_, or_, func, update, delete
from sqlalchemy.exc import SQLAlchemyError

from contract_api.domain.factory.organization_factory import OrganizationFactory
from contract_api.domain.models.offchain_service_attribute import OffchainServiceConfigDomain
from contract_api.domain.models.organization import OrganizationDomain
from contract_api.domain.models.service import ServiceDomain, NewServiceDomain
from contract_api.domain.models.service_endpoint import ServiceEndpointDomain, NewServiceEndpointDomain
from contract_api.domain.models.service_group import ServiceGroupDomain, NewServiceGroupDomain
from contract_api.domain.models.service_media import ServiceMediaDomain, NewServiceMediaDomain
from contract_api.domain.models.service_metadata import ServiceMetadataDomain, NewServiceMetadataDomain
from contract_api.domain.models.service_tag import ServiceTagDomain, NewServiceTagDomain
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

        return ServiceFactory.service_tags_from_db_model_list(tags_db)

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

        return ServiceFactory.service_media_from_db_model_list(service_media_db)

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

        return ServiceFactory.service_tags_from_db_model_list(service_tags_db)

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

    def get_service_metadata(self, org_id: str, service_id: str) -> ServiceMetadataDomain:
        query = select(
            ServiceMetadata
        ).where(
            ServiceMetadata.org_id == org_id,
            ServiceMetadata.service_id == service_id
        ).limit(1)

        result = self.session.execute(query)
        service_metadata_db = result.scalar_one_or_none()

        return ServiceFactory.service_metadata_from_db_model(service_metadata_db)

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

    def delete_services(self, org_id) -> None:
        query = delete(
            Service
        ).where(
            Service.org_id == org_id
        )
        self.session.execute(query)

        self.session.commit()

    def delete_service(self, org_id, service_id) -> None:
        query = delete(
            Service
        ).where(
            Service.org_id == org_id,
            Service.service_id == service_id
        )
        self.session.execute(query)

        self.session.commit()

    def get_services(self, org_id: str) -> list[ServiceDomain]:
        query = select(
            Service
        ).where(
            Service.org_id == org_id
        )

        result = self.session.execute(query)
        services_db = result.scalars().all()

        return ServiceFactory.services_from_db_model_list(services_db)

    def delete_service_dependents(self, org_id: str, service_id: str) -> None:
        self._delete_service_groups(org_id, service_id)
        self._delete_tags(org_id, service_id)
        self._delete_service_endpoints(org_id, service_id)

    def _delete_service_groups(self, org_id: str, service_id: str) -> None:
        query = delete(
            ServiceGroup
        ).where(
            ServiceGroup.org_id == org_id,
            ServiceGroup.service_id == service_id
        )

        self.session.execute(query)

    def _delete_tags(self, org_id: str, service_id: str) -> None:
        query = delete(
            ServiceTags
        ).where(
            ServiceTags.org_id == org_id,
            ServiceTags.service_id == service_id
        )

        self.session.execute(query)

    def _delete_service_endpoints(self, org_id: str, service_id: str) -> None:
        query = delete(
            ServiceEndpoint
        ).where(
            ServiceEndpoint.org_id == org_id,
            ServiceEndpoint.service_id == service_id
        )

        self.session.execute(query)

    def upsert_service(
            self,
            service: NewServiceDomain
    ) -> ServiceDomain:
        query = select(
            Service
        ).where(
            Service.org_id == service.org_id,
            Service.service_id == service.service_id
        ).limit(1)

        result = self.session.execute(query)
        service_db = result.scalar_one_or_none()

        if service_db:
            query = update(
                Service
            ).where(
                Service.org_id == service.org_id,
                Service.service_id == service.service_id
            ).values(
                hash_uri = service.hash_uri,
                is_curated = service.is_curated
            ).returning()

            self.session.execute(query)
            service_db = result.scalar_one()
        else:
            service_db = Service(
                org_id = service.org_id,
                service_id = service.service_id,
                hash_uri = service.hash_uri,
                is_curated = service.is_curated
            )

            self.session.add(service_db)
            self.session.refresh(service_db)

        return ServiceFactory.service_from_db_model(service_db)

    def upsert_service_metadata(
            self,
            service_metadata: NewServiceMetadataDomain
    ) -> ServiceMetadataDomain:
        query = select(
            ServiceMetadata
        ).where(
            ServiceMetadata.org_id == service_metadata.org_id,
            ServiceMetadata.service_id == service_metadata.service_id
        ).limit(1)

        result = self.session.execute(query)
        service_metadata_db = result.scalar_one_or_none()

        if service_metadata_db:
            query = update(
                ServiceMetadata
            ).where(
                ServiceMetadata.org_id == service_metadata.org_id,
                ServiceMetadata.service_id == service_metadata.service_id
            ).values(
                service_row_id = service_metadata.service_row_id,
                display_name = service_metadata.display_name,
                description = service_metadata.description,
                short_description = service_metadata.short_description,
                url = service_metadata.url,
                json = service_metadata.json,
                model_hash = service_metadata.model_hash,
                encoding = service_metadata.encoding,
                type = service_metadata.type,
                mpe_address = service_metadata.mpe_address,
                assets_url = service_metadata.assets_url,
                assets_hash = service_metadata.assets_hash,
                contributors = service_metadata.contributors
            ).returning()

            self.session.execute(query)
        else:
            service_metadata_db = ServiceMetadata(
                service_row_id = service_metadata.service_row_id,
                org_id = service_metadata.org_id,
                service_id = service_metadata.service_id,
                display_name = service_metadata.display_name,
                description = service_metadata.description,
                short_description = service_metadata.short_description,
                url = service_metadata.url,
                json = service_metadata.json,
                model_hash = service_metadata.model_hash,
                encoding = service_metadata.encoding,
                type = service_metadata.type,
                mpe_address = service_metadata.mpe_address,
                assets_url = service_metadata.assets_url,
                assets_hash = service_metadata.assets_hash,
                service_rating = service_metadata.service_rating,
                contributors = service_metadata.contributors
            )
            self.session.add(service_metadata_db)
            self.session.refresh(service_metadata_db)

        return ServiceFactory.service_metadata_from_db_model(service_metadata_db)

    def upsert_service_group(self, service_group: NewServiceGroupDomain) -> ServiceGroupDomain:
        query = select(
            ServiceGroup
        ).where(
            ServiceGroup.org_id == service_group.org_id,
            ServiceGroup.service_id == service_group.service_id,
            ServiceGroup.group_id == service_group.group_id
        ).limit(1)

        result = self.session.execute(query)
        service_group_db = result.scalar_one_or_none()

        if service_group_db:
            query = update(
                ServiceGroup
            ).where(
                ServiceGroup.org_id == service_group.org_id,
                ServiceGroup.service_id == service_group.service_id,
                ServiceGroup.group_id == service_group.group_id
            ).values(
                service_row_id = service_group.service_row_id,
                group_name = service_group.group_name,
                pricing = service_group.pricing,
                free_call_signer_address = service_group.free_call_signer_address,
                free_calls = service_group.free_calls
            ).returning()
            self.session.execute(query)
            service_group_db = result.scalar_one()
        else:
            service_group_db = ServiceGroup(
                service_row_id = service_group.service_row_id,
                org_id = service_group.org_id,
                service_id = service_group.service_id,
                group_id = service_group.group_id,
                group_name = service_group.group_name,
                pricing = service_group.pricing,
                free_call_signer_address = service_group.free_call_signer_address,
                free_calls = service_group.free_calls
            )
            self.session.add(service_group_db)
            self.session.refresh(service_group_db)

        return ServiceFactory.service_group_from_db_model(service_group_db)

    def upsert_service_endpoint(
            self,
            service_endpoint: NewServiceEndpointDomain
    ) -> ServiceEndpointDomain:
        query = select(
            ServiceEndpoint
        ).where(
            ServiceEndpoint.org_id == service_endpoint.org_id,
            ServiceEndpoint.service_id == service_endpoint.service_id,
            ServiceEndpoint.group_id == service_endpoint.group_id
        ).limit(1)

        result = self.session.execute(query)
        service_endpoint_db = result.scalar_one_or_none()

        if service_endpoint_db:
            query = update(
                ServiceEndpoint
            ).where(
                ServiceEndpoint.org_id == service_endpoint.org_id,
                ServiceEndpoint.service_id == service_endpoint.service_id,
                ServiceEndpoint.group_id == service_endpoint.group_id
            ).values(
                service_row_id = service_endpoint.service_row_id,
                endpoint = service_endpoint.endpoint,
                is_available = service_endpoint.is_available
            ).returning()
            self.session.execute(query)
            service_endpoint_db = result.scalar_one()
        else:
            service_endpoint_db = ServiceEndpoint(
                service_row_id = service_endpoint.service_row_id,
                org_id = service_endpoint.org_id,
                service_id = service_endpoint.service_id,
                group_id = service_endpoint.group_id,
                endpoint = service_endpoint.endpoint,
                is_available = service_endpoint.is_available
            )
            self.session.add(service_endpoint_db)
            self.session.refresh(service_endpoint_db)

        return ServiceFactory.service_endpoint_from_db_model(service_endpoint_db)

    def create_service_tag(
            self,
            service_tag: NewServiceTagDomain
    ) -> ServiceTagDomain:
        query = select(
            ServiceTags
        ).where(
            ServiceTags.service_row_id == service_tag.service_row_id,
            ServiceTags.org_id == service_tag.org_id,
            ServiceTags.service_id == service_tag.service_id,
            ServiceTags.tag_name == service_tag.tag_name
        ).limit(1)

        result = self.session.execute(query)
        service_tag_db = result.scalar_one_or_none()

        if not service_tag_db:
            service_tag_db = ServiceTags(
                service_row_id = service_tag.service_row_id,
                org_id = service_tag.org_id,
                service_id = service_tag.service_id,
                tag_name = service_tag.tag_name
            )
            self.session.add(service_tag_db)
            self.session.refresh(service_tag_db)

        return ServiceFactory.service_tag_from_db_model(service_tag_db)

    def upsert_service_media(
            self,
            service_media: NewServiceMediaDomain
    ) -> ServiceMediaDomain:
        query = select(
            ServiceMedia
        ).where(
            ServiceMedia.org_id == service_media.org_id,
            ServiceMedia.service_id == service_media.service_id,
            ServiceMedia.asset_type == service_media.asset_type
        ).limit(1)

        result = self.session.execute(query)
        service_media_db = result.scalar_one_or_none()

        if service_media_db:
            query = update(
                ServiceMedia
            ).where(
                ServiceMedia.org_id == service_media.org_id,
                ServiceMedia.service_id == service_media.service_id,
                ServiceMedia.asset_type == service_media.asset_type
            ).values(
                service_row_id = service_media.service_row_id,
                url = service_media.url,
                order = service_media.order,
                file_type = service_media.file_type,
                alt_text = service_media.alt_text,
                hash_uri = service_media.hash_uri
            ).returning()
            self.session.execute(query)
            service_media_db = result.scalar_one()
        else:
            service_media_db = ServiceMedia(
                service_row_id = service_media.service_row_id,
                org_id = service_media.org_id,
                service_id = service_media.service_id,
                url = service_media.url,
                order = service_media.order,
                file_type = service_media.file_type,
                asset_type = service_media.asset_type,
                alt_text = service_media.alt_text,
                hash_uri = service_media.hash_uri
            )
            self.session.add(service_media_db)
            self.session.refresh(service_media_db)

        return ServiceFactory.service_media_from_db_model(service_media_db)


