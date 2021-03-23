from common.logger import get_logger
from web3 import Web3
import json

import os

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from common.s3_util import S3Util
from contract_api.consumers.event_consumer import EventConsumer

from contract_api.dao.organization_repository import OrganizationRepository
from contract_api.dao.service_repository import ServiceRepository

from common.repository import Repository
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.config import ASSETS_PREFIX, ASSETS_BUCKET_NAME, S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY

logger = get_logger(__name__)


class OrganizationEventConsumer(EventConsumer):
    _connection = Repository(NETWORK_ID, NETWORKS=NETWORKS)
    _organization_repository = OrganizationRepository(_connection)
    _service_repository = ServiceRepository(_connection)

    def __init__(self, ws_provider, ipfs_url, ipfs_port):
        self._ipfs_util = IPFSUtil(ipfs_url, ipfs_port)
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self._s3_util = S3Util(S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY)

    def on_event(self, event):
        pass

    def _push_asset_to_s3_using_hash(self, hash, org_id, service_id):
        io_bytes = self._ipfs_util.read_bytesio_from_ipfs(hash.lstrip("ipfs://"))
        filename = hash.split("/")[1]
        if service_id:
            s3_filename = ASSETS_PREFIX + "/" + org_id + "/" + service_id + "/" + filename
        else:
            s3_filename = ASSETS_PREFIX + "/" + org_id  + "/" + filename

        new_url = self._s3_util.push_io_bytes_to_s3(s3_filename,
                                                    ASSETS_BUCKET_NAME, io_bytes)
        return new_url

    def _get_new_assets_url(self, org_id, new_ipfs_data):
        new_assets_hash = new_ipfs_data.get('assets', {})
        existing_assets_hash = {}
        existing_assets_url = {}

        existing_organization = self._organization_repository.get_organization(org_id)
        if existing_organization:
            existing_assets_hash = json.loads(existing_organization["assets_hash"])
            existing_assets_url = json.loads(existing_organization["org_assets_url"])
        new_assets_url_mapping = self._comapre_assets_and_push_to_s3(existing_assets_hash, new_assets_hash,
                                                                     existing_assets_url, org_id,
                                                                     "")
        return new_assets_url_mapping

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
        org_metadata_uri = Web3.toText(blockchain_org_data[2]).rstrip("\x00").lstrip("ipfs://")
        ipfs_org_metadata = self._ipfs_util.read_file_from_ipfs(org_metadata_uri)

        logger.info(f"org_metadata_uri {org_metadata_uri}")

        return org_id, blockchain_org_data, ipfs_org_metadata, org_metadata_uri


class OrganizationCreatedEventConsumer(OrganizationEventConsumer):

    def on_event(self, event):
        org_id, blockchain_org_data, ipfs_org_metadata, org_metadata_uri = self._get_org_details_from_blockchain(event)

        self._process_organization_create_update_event(org_id, blockchain_org_data, ipfs_org_metadata,
                                                       org_metadata_uri)

    def _process_organization_create_update_event(self, org_id, org_data, ipfs_org_metadata, org_metadata_uri):

        try:
            if (org_data is not None and org_data[0]):
                self._organization_repository.begin_transaction()

                new_assets_hash = ipfs_org_metadata.get('assets', {})
                new_assets_url_mapping = self._get_new_assets_url(org_id, ipfs_org_metadata)
                description = ipfs_org_metadata.get('description', "")
                contacts= ipfs_org_metadata.get('contacts', {})

                self._organization_repository.create_or_updatet_organization(
                    org_id=org_id, org_name=ipfs_org_metadata["org_name"], owner_address=org_data[3],
                    org_metadata_uri=org_metadata_uri, description=json.dumps(description),
                    assets_hash=json.dumps(new_assets_hash),
                    assets_url=json.dumps(new_assets_url_mapping),contacts=json.dumps(contacts))
                self._organization_repository.delete_organization_groups(org_id=org_id)
                self._organization_repository.create_organization_groups(
                    org_id=org_id, groups=ipfs_org_metadata["groups"])
                self._organization_repository.del_members(org_id=org_id)
                # self.organization_dao.create_or_update_members(org_id, org_data[4])
                self._organization_repository.commit_transaction()

        except Exception as e:
            self._organization_repository.rollback_transaction()
            raise e


class OrganizationModifiedEventConsumer(OrganizationCreatedEventConsumer):
    pass


class OrganizationDeletedEventConsumer(OrganizationEventConsumer):

    def on_event(self, event):
        org_id, blockchain_org_data, ipfs_org_metadata, org_metadata_uri = self._get_org_details_from_blockchain(event)
        self._process_organization_delete_event(org_id)

    def _process_organization_delete_event(self, org_id):
        try:
            self._connection.begin_transaction()
            self._organization_repository.delete_organization(org_id=org_id)
            self._organization_repository.delete_organization_groups(org_id=org_id)
            services = self._service_repository.get_services(org_id=org_id)
            for service in services:
                self._service_repository.delete_service_dependents(
                    org_id=org_id, service_id=service['service_id'])
                self._service_repository.delete_service(
                    org_id=org_id, service_id=service['service_id'])

            self._connection.commit_transaction()
        except Exception as e:
            logger.exception(str(e))
            self._connection.rollback_transaction()
            raise e

