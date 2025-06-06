from registry.application.schemas.service import CreateServiceRequest
from registry.constants import DEFAULT_SERVICE_RANKING, ServiceStatus, ServiceType
from registry.domain.models.offchain_service_config import OffchainServiceConfig
from registry.domain.models.service import Service
from registry.domain.models.service_comment import ServiceComment
from registry.domain.models.service_group import ServiceGroup
from registry.domain.models.service_state import ServiceState
from registry.exceptions import InvalidServiceStateException
from registry.infrastructure.models import (
    Service as ServiceDBModel,
    ServiceGroup as ServiceGroupDBModel,
    ServiceReviewHistory,
    ServiceState as ServiceStateDBModel,
)


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
            metadata_uri=service.metadata_uri,
            storage_provider=service.storage_provider,
            assets=service.assets,
            rating=service.rating,
            ranking=service.ranking,
            contributors=service.contributors,
            tags=service.tags,
            mpe_address=service.mpe_address,
            service_type=service.service_type,
            service_state=ServiceFactory.convert_service_state_from_db(service.service_state),
            groups=[ServiceGroup(org_uuid=group.org_uuid, service_uuid=group.service_uuid, group_id=group.group_id,
                                 group_name=group.group_name, endpoints=group.endpoints,
                                 test_endpoints=group.test_endpoints, pricing=group.pricing,
                                 free_calls=group.free_calls, daemon_address=group.daemon_address,
                                 free_call_signer_address=group.free_call_signer_address)
                    for group in service.groups]
        )

    @staticmethod
    def convert_service_state_from_db(service_state: ServiceStateDBModel):
        return ServiceState(
            service_state.org_uuid,
            service_state.service_uuid,
            service_state.state,
            service_state.transaction_hash
        )

    @staticmethod
    def convert_service_entity_model_to_db_model(username, service):
        return ServiceDBModel(
            org_uuid=service.org_uuid,
            uuid=service.uuid,
            display_name=service.display_name,
            service_id=service.service_id,
            metadata_uri=service.metadata_uri,
            storage_provider=service.storage_provider,
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
            service_type=service.service_type,
            groups=[ServiceFactory.convert_service_group_entity_model_to_db_model(group) for group in service.groups],
            service_state=ServiceFactory.convert_service_state_entity_model_to_db_model(
                username,
                service.service_state
            ),
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
            test_endpoints=service_group.test_endpoints,
            daemon_address=service_group.daemon_address,
            free_calls=service_group.free_calls,
            free_call_signer_address=service_group.free_call_signer_address,
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
        )

    @staticmethod
    def convert_service_review_history_entity_model_to_db_model(service_review_history):
        return ServiceReviewHistory(
            org_uuid=service_review_history.org_uuid,
            service_uuid=service_review_history.service_uuid,
            service_metadata=service_review_history.service_metadata,
            state=service_review_history.state,
            reviewed_by=service_review_history.reviewed_by,
            reviewed_on=service_review_history.reviewed_on,
            created_on=service_review_history.created_on,
            updated_on=service_review_history.updated_on
        )

    @staticmethod
    def create_service_entity_model_from_request(
        request: CreateServiceRequest,
        service_uuid: str,
        service_state: str
    ) -> Service:
        service_state_entity_model = ServiceFactory.create_service_state_entity_model(
            request.org_uuid, service_uuid, service_state
        )

        service_group_entity_model_list = [
            ServiceFactory.create_service_group_entity_model(
                request.org_uuid, service_uuid, group
            ) for group in request.groups
        ]

        contributors = []
        for contributor in request.contributors:
            if ServiceFactory.is_valid_contributor(contributor):
                contributors.append(contributor)

        return Service(
            request.org_uuid,
            service_uuid,
            request.service_id,
            request.display_name,
            request.short_description,
            request.description,
            request.project_url,
            request.proto,
            request.assets,
            request.ranking,
            request.rating,
            contributors,
            request.tags,
            request.mpe_address,
            request.metadata_uri,
            request.storage_provider,
            request.service_type,
            service_group_entity_model_list,
            service_state_entity_model
        )

    @staticmethod
    def create_service_entity_model(org_uuid, service_uuid, payload, status):
        try:
            service_state = getattr(ServiceStatus, status).value
        except:
            raise InvalidServiceStateException()

        service_state_entity_model = ServiceFactory.create_service_state_entity_model(
            org_uuid, service_uuid, service_state)

        service_group_entity_model_list = [
            ServiceFactory.create_service_group_entity_model(org_uuid, service_uuid, group) for group in
            payload.get("groups", [])]

        service_id = payload.get("service_id", "")
        display_name = payload.get("display_name", "")
        short_description = payload.get("short_description", "")
        description = payload.get("description", "")
        project_url = payload.get("project_url", "")
        proto = payload.get("proto", {})
        assets = payload.get("assets", {})
        ranking = payload.get("ranking", DEFAULT_SERVICE_RANKING)
        rating = payload.get("rating", {})
        payload_contributors = payload.get("contributors", [])
        contributors = []
        for contributor in payload_contributors:
            if ServiceFactory.is_valid_contributor(contributor):
                contributors.append(contributor)

        tags = payload.get("tags", [])
        mpe_address = payload.get("mpe_address", "")
        service_type = payload.get("service_type", ServiceType.GRPC.value)
        metadata_uri = payload.get("metadata_uri", "")
        storage_provider = payload.get("storage_provider", "")
        return Service(
            org_uuid, service_uuid, service_id, display_name, short_description, description, project_url, proto,
            assets, ranking, rating, contributors, tags, mpe_address, metadata_uri, storage_provider,
            service_type, service_group_entity_model_list, service_state_entity_model)

    @staticmethod
    def is_valid_contributor(contributor):
        if (contributor["email_id"] is None or len(contributor["email_id"]) == 0) and \
                (contributor["name"] is None or len(contributor["name"]) == 0):
            return False
        return True

    @staticmethod
    def create_service_state_entity_model(org_uuid, service_uuid, state, transaction_hash=None):
        return ServiceState(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            state=state,
            transaction_hash=transaction_hash
        )

    @staticmethod
    def convert_offchain_service_config_db_model_to_entity_model(org_uuid, service_uuid, offchain_service_configs_db):
        configs = {}
        for offchain_service_config_db in offchain_service_configs_db:
            if offchain_service_config_db[3] == "demo_component_required":
                offchain_service_config_db[4] == int(offchain_service_config_db[4])
            configs.update({offchain_service_config_db[3]: int(offchain_service_config_db[4])})
        return OffchainServiceConfig(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            configs=configs
        )

    @staticmethod
    def create_service_group_entity_model(org_uuid, service_uuid, group):
        return ServiceGroup(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            group_id=group["group_id"],
            group_name=group.get("group_name", ""),
            pricing=group.get("pricing", []),
            endpoints=group.get("endpoints", {}),
            test_endpoints=group.get("test_endpoints", []),
            daemon_address=group.get("daemon_addresses", []),
            free_calls=group.get("free_calls", 0),
            free_call_signer_address=group.get("free_call_signer_address", None),
        )

    @staticmethod
    def create_service_comment_entity_model(org_uuid, service_uuid, support_type, user_type, commented_by, comment):
        return ServiceComment(
            org_uuid=org_uuid,
            service_uuid=service_uuid,
            support_type=support_type,
            user_type=user_type,
            commented_by=commented_by,
            comment=comment
        )

    @staticmethod
    def convert_service_comment_db_model_to_entity_model(service_comment):
        if service_comment is None:
            return None
        return ServiceComment(
            org_uuid=service_comment.org_uuid,
            service_uuid=service_comment.service_uuid,
            support_type=service_comment.support_type,
            user_type=service_comment.user_type,
            commented_by=service_comment.commented_by,
            comment=service_comment.comment
        )

    @staticmethod
    def parse_service_metadata_assets(assets, existing_assets):
        if assets is None:
            assets = {}
        if existing_assets is None:
            existing_assets = {}
        url = ""
        for key, value in assets.items():
            if existing_assets and key in existing_assets:
                if existing_assets[key] and 'url' in existing_assets[key]:
                    url = existing_assets[key]['url']
            else:
                url = ""

            assets[key] = {
                "hash": value,
                "url": url
            }
        merged = {**existing_assets, **assets}
        return merged
