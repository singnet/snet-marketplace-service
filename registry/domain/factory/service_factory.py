from datetime import datetime as dt
from registry.domain.models.service import Service
from registry.infrastructure.models import Service as ServiceDBModel, ServiceGroup as ServiceGroupDBModel, \
    ServiceState as ServiceStateDBModel
from registry.domain.models.service_group import ServiceGroup
from registry.domain.models.service_state import ServiceState
from registry.constants import DEFAULT_SERVICE_RANKING, ServiceStatus, ServiceAvailabilityStatus


class ServiceFactory:

    @staticmethod
    def convert_service_db_model_to_entity_model(service):
        return Service(
            org_uuid=service.org_uuid,
            uuid=service.uuid,
            service_id=service.service_id,
            display_name=service.display_name,
            short_description=service.short_description,
            description=service.description,
            project_url=service.project_url,
            proto=service.proto,
            metadata_ipfs_hash=service.metadata_ipfs_hash,
            assets=service.assets,
            rating=service.rating,
            ranking=service.ranking,
            contributors=service.contributors,
            tags=service.tags,
            mpe_address=service.mpe_address,
            service_state=ServiceState(service.service_state.org_uuid, service.service_state.service_uuid,
                                       service.service_state.state, service.service_state.transaction_hash),
            groups=[ServiceGroup(org_uuid=group.org_uuid, service_uuid=group.service_uuid, group_id=group.group_id,
                                 group_name=group.group_name, endpoints=group.endpoints, pricing=group.pricing,
                                 free_calls=group.free_calls, daemon_address=group.daemon_address,
                                 free_call_signer_address=group.free_call_signer_address)
                    for group in service.groups]
        )

    @staticmethod
    def convert_service_entity_model_to_db_model(username, service):
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
            tags=service.tags,
            mpe_address=service.mpe_address,
            created_on=dt.utcnow(),
            groups=[ServiceFactory.convert_service_group_entity_model_to_db_model(group) for group in service.groups],
            service_state=ServiceFactory.convert_service_state_entity_model_to_db_model(username, service.service_state)
        )

    @staticmethod
    def convert_service_group_entity_model_to_db_model(service_group):
        return ServiceGroupDBModel(
            org_uuid=service_group.org_uuid,
            service_uuid=service_group.service_uuid,
            group_id=service_group.group_id,
            group_name=service_group.group_name,
            pricing=service_group.pricing,
            endpoints=service_group.endpoints,
            daemon_address=service_group.daemon_address,
            free_calls=service_group.free_calls,
            free_call_signer_address=service_group.free_call_signer_address,
            created_on=dt.utcnow(),
            updated_on=dt.utcnow()
        )

    @staticmethod
    def convert_service_state_entity_model_to_db_model(username, service_state):
        return ServiceStateDBModel(
            org_uuid=service_state.org_uuid,
            service_uuid=service_state.service_uuid,
            state=service_state.state,
            transaction_hash=service_state.transaction_hash,
            created_by=username,
            updated_by=username,
            approved_by="",
            created_on=dt.utcnow()

        )

    @staticmethod
    def create_service_entity_model(org_uuid, service_uuid, payload, status):
        service_state_entity_model = \
            ServiceFactory.create_service_state_entity_model(org_uuid, service_uuid,
                                                             getattr(ServiceStatus, status).value)
        service_group_entity_model_list = [
            ServiceFactory.create_service_group_entity_model(org_uuid, service_uuid, group) for group in
            payload.get("groups", [])]
        return Service(
            org_uuid, service_uuid, payload.get("service_id", ""), payload.get("display_name", ""),
            payload.get("short_description", ""), payload.get("description", ""), payload.get("project_url", ""),
            payload.get("proto", {}), payload.get("assets", {}), payload.get("ranking", DEFAULT_SERVICE_RANKING),
            payload.get("rating", {}), payload.get("contributors", []), payload.get("tags", []),
            payload.get("mpe_address", ""), payload.get("metadata_ipfs_hash", ""), service_group_entity_model_list,
            service_state_entity_model)

    @staticmethod
    def create_service_state_entity_model(org_uuid, service_uuid, state, transaction_hash=None):
        return ServiceState(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            state=state,
            transaction_hash=transaction_hash
        )

    @staticmethod
    def create_service_group_entity_model(org_uuid, service_uuid, group):
        return ServiceGroup(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            group_id=group["group_id"],
            group_name=group.get("group_name", ""),
            pricing=group.get("pricing", []),
            endpoints=group.get("endpoints", []),
            daemon_address=group.get("daemon_address", []),
            free_calls=group.get("free_calls", 0),
            free_call_signer_address=group.get("free_call_signer_address", None),
        )
