import json
from web3 import Web3

from common.logger import get_logger
from contract_api.application.consumers.event_consumer import RegistryEventConsumer
from contract_api.application.schemas.consumer_schemas import RegistryEventConsumerRequest

logger = get_logger(__name__)


class OrganizationCreatedEventConsumer(RegistryEventConsumer):
    def __init__(self):
        super().__init__()

    def on_event(self, request: RegistryEventConsumerRequest=None, org_id=None):
        if org_id is None:
            org_id = request.org_id
        org_id, blockchain_org_data, org_metadata, org_metadata_uri = (
            self._get_org_details_from_blockchain(org_id)
        )

        self._process_organization_create_update_event(
            org_id, blockchain_org_data, org_metadata, org_metadata_uri
        )


    def _process_organization_create_update_event(self, org_id, org_data, org_metadata, org_metadata_uri):

        if org_data is not None and org_data[0]:
            with self._organization_repository.session.begin():
                new_assets_hash = org_metadata.get("assets", {})
                new_assets_url_mapping = self._get_new_assets_url(org_id, org_metadata)
                description = org_metadata.get("description", "")
                contacts= org_metadata.get("contacts", {})

                self._organization_repository.create_or_updatet_organization(
                    org_id=org_id,
                    org_name=org_metadata["org_name"],
                    owner_address=org_data[3],
                    org_metadata_uri=org_metadata_uri,
                    is_curated=1,
                    description=json.dumps(description),
                    assets_hash=json.dumps(new_assets_hash),
                    assets_url=json.dumps(new_assets_url_mapping),
                    contacts=json.dumps(contacts)
                )
                self._organization_repository.delete_organization_groups(org_id=org_id)
                self._organization_repository.create_organization_groups(
                    org_id=org_id, groups=org_metadata["groups"])
                self._organization_repository.del_members(org_id=org_id)
                # self.organization_dao.create_or_update_members(org_id, org_data[4])
                self._organization_repository.commit_transaction()


    def _get_new_assets_url(self, org_id, new_ipfs_data):
        new_assets_hash = new_ipfs_data.get("assets", {})
        logger.info(f"New_assets_hash: {new_assets_hash}")
        existing_assets_hash = {}
        existing_assets_url = {}

        existing_organization = self._organization_repository.get_organization(org_id)
        if existing_organization:
            existing_assets_hash = json.loads(existing_organization["assets_hash"])
            logger.info(f"Existing_assets_hash: {existing_assets_hash}")
            existing_assets_url = json.loads(existing_organization["org_assets_url"])
            logger.info(f"Existing_assets_url: {existing_assets_url}")
        new_assets_url_mapping = self._compare_assets_and_push_to_s3(
            existing_assets_hash,
            new_assets_hash,
            existing_assets_url,
            org_id,
            ""
        )
        return new_assets_url_mapping

    def _get_org_details_from_blockchain(self, org_id):
        registry_contract = self._get_contract("REGISTRY")

        logger.info(f"Organization id: {org_id}")
        encoded_org_id = Web3.to_bytes(text = org_id).ljust(32, b'\0')[:32]
        logger.info(f"Encoded organization id: {encoded_org_id}")
        blockchain_org_data = registry_contract.functions.getOrganizationById(
            encoded_org_id
        ).call()

        org_metadata_uri = Web3.to_text(blockchain_org_data[2]).rstrip("\x00")
        logger.info(f"Organization metadata uri hash: {org_metadata_uri}")

        org_metadata = self._storage_provider.get(org_metadata_uri)

        return org_id, blockchain_org_data, org_metadata, org_metadata_uri


class OrganizationDeletedEventConsumer(RegistryEventConsumer):
    def __init__(self):
        super().__init__()

    def on_event(self, request: RegistryEventConsumerRequest, org_id=None):
        if org_id is None:
            org_id = request.org_id
        self._organization_repository.delete_organization(org_id)


