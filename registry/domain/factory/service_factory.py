from registry.domain.models.service import Service
from registry.domain.models.service_group import ServiceGroup


class ServiceFactory:

    @staticmethod
    def convert_service_db_model_to_entity_model(service):
        return Service(
            org_uuid=service.Service.org_uuid,
            uuid=service.Service.uuid,
            service_id=service.Service.service_id,
            display_name=service.Service.display_name,
            short_description=service.Service.short_description,
            description=service.Service.description,
            project_url=service.Service.project_url,
            proto=service.Service.proto,
            metadata_ipfs_hash=service.Service.metadata_ipfs_hash,
            assets=service.Service.assets,
            rating=service.Service.rating,
            ranking=service.Service.ranking,
            contributors=service.Service.contributors,
            groups=[ServiceGroup(org_uuid=group.org_uuid, service_uuid=group.service_uuid, group_id=group.group_id,
                                 endpoints=group.endpoints, pricing=group.pricing) for group in service.Service.groups]
        )
