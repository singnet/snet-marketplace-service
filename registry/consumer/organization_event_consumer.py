import traceback

from common.logger import get_logger
from web3 import Web3

import os

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from common.s3_util import S3Util
from contract_api.consumers.event_consumer import EventConsumer

from registry.config import S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY, NETWORK_ID
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository

logger = get_logger(__name__)

from deepdiff import DeepDiff


class OrganizationEventConsumer(EventConsumer):
    _organization_repository = OrganizationRepository()

    def __init__(self, ws_provider, ipfs_url, ipfs_port):
        self._ipfs_util = IPFSUtil(ipfs_url, ipfs_port)
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self._s3_util = S3Util(S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY)

    def on_event(self, event):
        pass

    def _get_org_id_from_event(self, event):
        event_org_data = eval(event['data']['json_str'])
        org_id_bytes = event_org_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\x00")
        return org_id

    def _get_registry_contract(self):
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'node_modules', 'singularitynet-platform-contracts'))
        registry_contract = self._blockchain_util.get_contract_instance(base_contract_path, "REGISTRY", net_id)

        return registry_contract

    def _get_org_details_from_blockchain(self, event):
        logger.info(f"processing org event {event}")

        registry_contract = self._get_registry_contract()
        org_id = self._get_org_id_from_event(event)

        blockchain_org_data = registry_contract.functions.getOrganizationById(org_id.encode('utf-8')).call()
        org_metadata_uri = Web3.toText(blockchain_org_data[2])[7:].rstrip("\u0000")
        ipfs_org_metadata = self._ipfs_util.read_file_from_ipfs(org_metadata_uri)

        return org_id, ipfs_org_metadata


class OrganizationCreatedEventConsumer(OrganizationEventConsumer):

    def on_event(self, event):
        org_id, ipfs_org_metadata = self._get_org_details_from_blockchain(event)
        self._process_organization_create_event(org_id, ipfs_org_metadata)

    def _process_organization_create_event(self, org_id, ipfs_org_metadata):
        try:
            persisted_publish_in_progress_organization = self._organization_repository.get_org_with_status_using_org_id(
                org_id, "PUBLISH_IN_PROGRESS")
            if len(persisted_publish_in_progress_organization) == 0:
                raise Exception("This organization is not published through publisher portla")
            existing_publish_in_progress_organization = OrganizationFactory.parse_organization_data_model(
                persisted_publish_in_progress_organization[0].Organization)
            recieved_organization_event = OrganizationFactory.parse_organization_metadata(
                existing_publish_in_progress_organization.org_uuid, ipfs_org_metadata)

            org_diff = DeepDiff(existing_publish_in_progress_organization, recieved_organization_event)

            if not org_diff:
                self._organization_repository.change_org_status(existing_publish_in_progress_organization.org_uuid,
                                                                "PUBLISH_IN_PROGRESS", "PUBLISHED", "blockchain_event")
            else:
                raise Exception("Event data is not same as it was published through publisher portal")
        except Exception as e:
            print(traceback)
            raise Exception("Error while processing org created event")


class OrganizationModifiedEventConsumer(OrganizationEventConsumer):
    def on_event(self, event):
        org_id, ipfs_org_metadata = self._get_org_details_from_blockchain(event)
        self._process_organization_create_update_event(org_id, ipfs_org_metadata)

    def _process_organization_update_event(self, org_id, ipfs_org_metadata):
        # In case of update one orgnaization record will be in published state
        # and one org record(latest changes) will be in publish in progress

        persisted_publish_in_progress_organization = self._organization_repository.get_org_with_status_using_org_id(
            org_id, "PUBLISH_IN_PROGRESS")
        persisted_published_organization = self._organization_repository.get_org_with_status_using_org_id(org_id,
                                                                                                          "PUBLISHED")
        existing_publish_in_progress_organization = OrganizationFactory.parse_organization_data_model(
            persisted_publish_in_progress_organization)
        existing_published_organization = OrganizationFactory.parse_organization_data_model(
            persisted_publish_in_progress_organization)
        recieved_organization_event = OrganizationFactory.parse_organization_metadata(ipfs_org_metadata)

        org_diff = DeepDiff(existing_publish_in_progress_organization, recieved_organization_event)

        if not org_diff:
            # Move current published org record to  archive table marks this record as published
            self._organization_repository.export_org_with_status(existing_published_organization, "PUBLISHED")
            self._organization_repository.change_org_status(existing_publish_in_progress_organization.org_uuid,
                                                            "PUBLISHED")


if __name__ == '__main__':
    payload = {
        "org_id": "",
        "org_uuid": "",
        "org_name": "dummy_org",
        "org_type": "individual",
        "metadata_ipfs_hash": "",
        "description": "that is the dummy org for testcases",
        "short_description": "that is the short description",
        "url": "https://dummy.dummy",
        "contacts": [],
        "assets": {"hero_iamge": {"test": 12344}}
    }

    payload1 = {
        "org_id": "",
        "org_uuid": "",
        "org_name": "dummy_org",
        "org_type": "individual",
        "metadata_ipfs_hash": "",
        "description": "that is the dummy org for testcases",
        "short_description": "that is the short description",
        "url": "https://dummy.dummy",
        "contacts": [],
        "assets": {"hero_iamge": {"test": 1234}}
    }
    org1 = OrganizationFactory.parse_raw_organization(payload)

    org2 = OrganizationFactory.parse_raw_organization(payload1)

    ddiff = DeepDiff(org1, org2)
    print(ddiff)
