from datetime import datetime as dt
from registry.domain.models.service import Service
from registry.infrastructure.models.models import Service as ServiceDBModel
from registry.domain.models.service_group import ServiceGroup
from registry.constants import DEFAULT_SERVICE_RANKING, ServiceStatus


class ServiceFactory:

    @staticmethod
    def convert_service_db_model_to_entity_model(service):
        return Service(
            org_uuid=service.Service.org_uuid,
            uuid=service.Service.uuid,
            service_id=service.Service.service_id,
            display_name=service.Service.display_name,
            state=service.ServiceReviewWorkflow.state,
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

    @staticmethod
    def convert_entity_model_to_service_db_model(service):
        return ServiceDBModel(
            org_uuid=service.org_uuid,
            uuid=service.uuid,
            display_name=service.display_name,
            service_id=service.service_id,
            metadata_ipfs_hash=service.metadata_ipfs_hash,
            proto=service.proto,
            short_description=service.short_description,
            description=service.description,
            project_url=service.project_url,
            assets=service.assets,
            rating=service.rating,
            ranking=service.ranking,
            contributors=service.contributors,
            created_on=dt.utcnow(),
            updated_on=dt.utcnow(),
            groups=service.groups
        )

    @staticmethod
    def create_service_entity_model(org_uuid, service_uuid, payload):
        return Service(
            org_uuid, service_uuid, payload.get("service_id", ""), payload.get("display_name", ""),
            payload.get("short_description", ""), payload.get("description", ""), payload.get("project_url", ""),
            payload.get("proto", {}), payload.get("assets", {}), payload.get("ranking", DEFAULT_SERVICE_RANKING),
            payload.get("rating", {}), payload.get("contributors", []), payload.get("metadata_ipfs_hash", ""),
            payload.get("groups", []), ServiceStatus.DRAFT.value)
