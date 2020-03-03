from datetime import datetime as dt
from registry.domain.models.service import Service
from registry.infrastructure.models import Service as ServiceDBModel, ServiceGroup as ServiceGroupDBModel, \
    ServiceState as ServiceStateDBModel, ServiceReviewHistory
from registry.domain.models.service_group import ServiceGroup
from registry.domain.models.service_state import ServiceState
from registry.constants import DEFAULT_SERVICE_RANKING, ServiceStatus, ServiceAvailabilityStatus


class ServiceFactory:

    @staticmethod
    def convert_service_db_model_to_entity_model(service):
        if service is None:
            return None
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
            assets=service.assets,
            rating=service.rating,
            ranking=service.ranking,
            contributors=service.contributors,
            tags=service.tags,
            mpe_address=service.mpe_address,
            service_state=ServiceState(service.service_state.org_uuid, service.service_state.service_uuid,
                                       service.service_state.state, service.service_state.transaction_hash),
            groups=[ServiceGroup(org_uuid=group.org_uuid, service_uuid=group.service_uuid, group_id=group.group_id,
                                 group_name=group.group_name, endpoints=group.endpoints,
                                 test_endpoints=group.test_endpoints, pricing=group.pricing,
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
            metadata_uri=service.metadata_uri,
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
            test_endpoints=service_group.test_endpoints,
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
            payload.get("mpe_address", ""), payload.get("metadata_uri", ""), service_group_entity_model_list,
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
            test_endpoints=group.get("test_endpoints", []),
            daemon_address=group.get("daemon_address", []),
            free_calls=group.get("free_calls", 0),
            free_call_signer_address=group.get("free_call_signer_address", None),
        )

    @staticmethod
    def create_service_from_service_metadata(org_uuid, service_uuid, service_metadata, tags_data, status):
        # s={
        #     "version": 1,
        #     "display_name": "Entity Disambiguation",
        #     "encoding": "proto",
        #     "service_type": "grpc",
        #     "model_ipfs_hash": "Qmd21xqgX8fkU4fD2bFMNG2Q86wAB4GmGBekQfLoiLtXYv",
        #     "mpe_address": "0x34E2EeE197EfAAbEcC495FdF3B1781a3b894eB5f",
        #     "groups": [
        #         {
        #             "group_name": "default_group",
        #             "free_calls": 12,
        #             "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
        #             "daemon_address ": ["0x1234", "0x345"],
        #             "pricing": [
        #                 {
        #                     "price_model": "fixed_price",
        #                     "price_in_cogs": 1,
        #                     "default": True
        #                 }
        #             ],
        #             "endpoints": [
        #                 "https://tz-services-1.snet.sh:8005"
        #             ],
        #             "group_id": "EoFmN3nvaXpf6ew8jJbIPVghE5NXfYupFF7PkRmVyGQ="
        #         }
        #     ],
        #     "assets": {
        #         "hero_image": "Qmb1n3LxPXLHTUMu7afrpZdpug4WhhcmVVCEwUxjLQafq1/hero_named-entity-disambiguation.png"
        #     },
        #     "service_description": {
        #         "url": "https://singnet.github.io/nlp-services-misc/users_guide/named-entity-disambiguation-service.html",
        #         "description": "Provide further clearity regaridng entities named within a piece of text. For example, \"Paris is the capital of France\", we would want to link \"Paris\" to Paris the city not Paris Hilton in this case.",
        #         "short_description": "text of 180 chars"
        #     },
        #     "contributors": [
        #         {
        #             "name": "dummy dummy",
        #             "email_id": "dummy@dummy.io"
        #         }
        #     ]
        # }
        service_state_entity_model = \
            ServiceFactory.create_service_state_entity_model(org_uuid, service_uuid,
                                                             getattr(ServiceStatus, status).value)
        service_group_entity_model_list = [
            ServiceFactory.create_service_group_entity_model("", service_uuid, group) for group in
            service_metadata.get("groups", [])]
        return Service(
            org_uuid, service_uuid, service_metadata.get("service_id", ""), service_metadata.get("display_name", ""),
            service_metadata.get("short_description", ""), service_metadata.get("description", ""),
            service_metadata.get("project_url", ""),
            service_metadata.get("proto", {}), service_metadata.get("assets", {}),
            service_metadata.get("ranking", DEFAULT_SERVICE_RANKING),
            service_metadata.get("rating", {}), service_metadata.get("contributors", []),
            tags_data,
            service_metadata.get("mpe_address", ""), service_metadata.get("metadata_ipfs_hash", ""),
            service_group_entity_model_list,
            service_state_entity_model)
