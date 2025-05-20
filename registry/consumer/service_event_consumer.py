import ast
import json
import os
from uuid import uuid4

from web3 import Web3

from common import blockchain_util, boto_utils
from common.constant import StatusCode
from common.logger import get_logger

from registry.settings import settings
from registry.constants import (
    DEFAULT_SERVICE_RANKING,
    ServiceStatus,
    SmartContracts,
)
from registry.domain.factory.service_factory import ServiceFactory
from registry.domain.models.service import Service
from registry.infrastructure.storage_provider import StorageProvider
from registry.exceptions import ServiceNotFoundException

logger = get_logger(__name__)
BLOCKCHAIN_USER = "BLOCKCHAIN_USER"
NETWORK_ID = settings.network.id
CONTRACT_BASE_PATH = settings.network.networks[NETWORK_ID].contract_base_path


class ServiceEventConsumer:
    def __init__(self, ws_provider, service_repository, organization_repository):
        self._blockchain_util = blockchain_util.BlockChainUtil(
            "WS_PROVIDER", ws_provider
        )
        self._service_repository = service_repository
        self._organization_repository = organization_repository
        self._storage_provider = StorageProvider()

    def on_event(self, event):
        pass

    def _fetch_tags(self, registry_contract, org_id_hex, service_id_hex):
        tags_data = registry_contract.functions.getServiceRegistrationById(
            org_id_hex, service_id_hex
        ).call()

        str_tag_data = []
        for tag in tags_data[3]:
            str_tag_data.append(Web3.to_text(tag).rstrip("\x00"))
        return str_tag_data

    def _get_org_id_from_event(self, event):
        event_data = event["data"]
        service_data = ast.literal_eval(event_data["json_str"])
        org_id_bytes = service_data["orgId"]
        org_id = Web3.to_text(org_id_bytes).rstrip("\x00")
        return org_id

    def _get_transaction_hash(self, event):
        return event["data"]["transaction_hash"]

    def _get_service_id_from_event(self, event):
        event_data = event["data"]
        service_data = ast.literal_eval(event_data["json_str"])
        service_id_bytes = service_data["serviceId"]
        service_id = Web3.to_text(service_id_bytes).rstrip("\x00")
        return service_id

    def _get_metadata_uri_from_event(self, event):
        event_data = event["data"]
        service_data = ast.literal_eval(event_data["json_str"])
        metadata_uri = Web3.to_text(service_data["metadataURI"]).rstrip("\u0000")
        return metadata_uri

    def _get_base_contract_path(self):
        return os.path.abspath(
            os.path.join(
                f"{CONTRACT_BASE_PATH}/node_modules/singularitynet-platform-contracts"
            )
        )

    def _get_registry_contract(self):
        base_contract_path = self._get_base_contract_path()
        registry_contract = self._blockchain_util.get_contract_instance(
            base_contract_path,
            SmartContracts.REGISTRY.value,
            NETWORK_ID,
            settings.token_name,
            settings.stage,
        )

        return registry_contract

    def _get_service_details_from_blockchain(self, event):
        logger.info(f"processing service event {event}")

        registry_contract = self._get_registry_contract()
        org_id = self._get_org_id_from_event(event)
        service_id = self._get_service_id_from_event(event)

        # tags_data = self._fetch_tags(
        #     registry_contract=registry_contract, org_id_hex=org_id.encode("utf-8"),
        #     service_id_hex=service_id.encode("utf-8"))
        transaction_hash = self._get_transaction_hash(event)

        return org_id, service_id, transaction_hash


class ServiceCreatedEventConsumer(ServiceEventConsumer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_event(self, event):
        org_id, service_id, transaction_hash = (
            self._get_service_details_from_blockchain(event)
        )
        metadata_uri = self._get_metadata_uri_from_event(event)
        service_data = self._storage_provider.get(metadata_uri)
        self._process_service_data(
            org_id=org_id,
            service_id=service_id,
            service_metadata=service_data,
            transaction_hash=transaction_hash,
            metadata_uri=metadata_uri,
        )

    def _get_existing_service_details(self, org_id, service_id):
        try:
            existing_service = self._service_repository.get_service_for_given_service_id_and_org_id(
                org_id, service_id
            )
        except ServiceNotFoundException:
            existing_service = None

        org_uuid = self._organization_repository.get_organization().uuid

        return org_uuid, existing_service

    def _is_same_transaction(self):
        pass

    def _add_validation_attribute_to_endpoint(self, groups):
        for group in groups:
            changed_endpoints = {}
            for endpoint in group["endpoints"]:
                changed_endpoints[endpoint] = {"valid": False}
            group["endpoints"] = changed_endpoints

    def _process_service_data(
        self, org_id, service_id, service_metadata, transaction_hash, metadata_uri
    ):
        org_uuid, existing_service = self._get_existing_service_details(
            org_id, service_id
        )
        service_uuid = str(uuid4())
        display_name = service_metadata.get("display_name", "")
        description_dict = service_metadata.get("service_description", {})
        short_description = description_dict.get("short_description", "")
        description = description_dict.get("description", "")
        project_url = description_dict.get("url", "")
        proto = {
            "encoding": service_metadata.get("encoding", ""),
            "service_type": service_metadata.get("service_type", ""),
            "model_hash": service_metadata.get("service_api_source", ""),
        }
        assets = service_metadata.get("assets", {})
        mpe_address = service_metadata.get("mpe_address", "")
        contributors = service_metadata.get("contributors", [])
        tags_data = service_metadata.get("tags", [])
        service_type = service_metadata.get("service_type", "grpc")
        state = ServiceFactory.create_service_state_entity_model(
            org_uuid, service_uuid, getattr(ServiceStatus, "PUBLISHED_UNAPPROVED").value
        )

        self._add_validation_attribute_to_endpoint(service_metadata.get("groups", []))
        groups = [
            ServiceFactory.create_service_group_entity_model(
                org_uuid, service_uuid, group
            )
            for group in service_metadata.get("groups", [])
        ]

        storage_provider, _ = self._storage_provider.uri_to_hash(metadata_uri)
        storage_provider = storage_provider.value

        if existing_service:
            existing_service.display_name = display_name
            existing_service.short_description = short_description
            existing_service.description = description
            existing_service.project_url = project_url
            existing_service.proto = proto
            existing_service.assets = ServiceFactory.parse_service_metadata_assets(
                assets, existing_service.assets
            )
            existing_service.mpe_address = mpe_address
            existing_service.metadata_uri = metadata_uri
            existing_service.contributors = contributors
            existing_service.tags = tags_data
            existing_service.groups = [
                ServiceFactory.create_service_group_entity_model(
                    org_uuid, existing_service.uuid, group
                )
                for group in service_metadata.get("groups", [])
            ]
            existing_service.storage_provider = storage_provider

        received_service = Service(
            org_uuid=org_uuid,
            uuid=str(uuid4()),
            service_id=service_id,
            display_name=display_name,
            short_description=short_description,
            description=description,
            project_url=project_url,
            proto=proto,
            assets=assets,
            ranking=DEFAULT_SERVICE_RANKING,
            rating={},
            contributors=contributors,
            tags=tags_data,
            mpe_address=mpe_address,
            metadata_uri=metadata_uri,
            service_type=service_type,
            groups=groups,
            service_state=state,
            storage_provider=storage_provider,
        )

        if not existing_service:
            self._service_repository.add_service(received_service, BLOCKCHAIN_USER)
        elif existing_service.service_state.transaction_hash is None:
            self._service_repository.save_service(
                BLOCKCHAIN_USER, existing_service, ServiceStatus.DRAFT.value
            )
        elif existing_service.service_state.transaction_hash != transaction_hash:
            # TODO:  Implement major & minor changes
            self._service_repository.save_service(
                BLOCKCHAIN_USER, existing_service, ServiceStatus.DRAFT.value
            )
        elif existing_service.service_state.transaction_hash == transaction_hash:
            self.__curate_service_in_marketplace(service_id, org_id, curated=True)
            self._service_repository.save_service(
                BLOCKCHAIN_USER, existing_service, ServiceStatus.PUBLISHED.value
            )

    @staticmethod
    def __curate_service_in_marketplace(service_id, org_id, curated):
        curate_service_payload = {
            "pathParameters": {"orgId": org_id, "serviceId": service_id},
            "queryStringParameters": {"curate": str(curated)},
            "body": None,
        }

        curate_service_response = boto_utils.BotoUtils(
            region_name=settings.aws.REGION_NAME
        ).invoke_lambda(
            lambda_function_arn=settings.lambda_arn.SERVICE_CURATE_ARN,
            invocation_type="RequestResponse",
            payload=json.dumps(curate_service_payload),
        )

        if curate_service_response["statusCode"] != StatusCode.CREATED:
            logger.info(
                f"failed to update service ({service_id}, {org_id}) curation {curate_service_response}"
            )
            raise Exception("failed to update service curation")
