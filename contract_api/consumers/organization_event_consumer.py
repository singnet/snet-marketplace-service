from common.logger import get_logger
from web3 import Web3

import os

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from common.s3_util import S3Util
from consumers.event_consumer import EventConsumer

from contract_api.dao.organization_repository import OrganizationRepository
from contract_api.dao.service_repository import ServiceRepository

from common.repository import Repository
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.config import ASSETS_PREFIX, ASSETS_BUCKET_NAME, S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY
logger = get_logger(__name__)


class OrganizationEventConsumer(EventConsumer):
    connection = Repository(NETWORK_ID, NETWORKS=NETWORKS)
    organization_repository = OrganizationRepository(connection)
    service_repository = ServiceRepository(connection)

    def __init__(self, ws_provider, ipfs_url, ipfs_port):
        self.ipfs_util = IPFSUtil(ipfs_url, ipfs_port)
        self.blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self.s3_util = S3Util(S3_BUCKET_ACCESS_KEY, S3_BUCKET_SECRET_KEY)



    def _push_asset_to_s3_using_hash(self, hash, org_id, service_id):
        io_bytes = self.ipfs_util.read_bytesio_from_ipfs(hash)
        filename = hash.split("/")[1]
        if service_id:
            s3_filename = ASSETS_PREFIX + "/" + org_id + "/" + service_id + "/" + filename
        else:
            s3_filename = ASSETS_PREFIX + "/" + org_id + "/" + service_id + "/" + filename

        new_url = self.s3_util.push_io_bytes_to_s3(s3_filename,
                                                   ASSETS_BUCKET_NAME, io_bytes)
        return new_url

    def _get_new_assets_url(self, org_id, new_ipfs_data):
        new_assets_hash = new_ipfs_data.get('assets', {})
        existing_assets_hash = {}
        existing_assets_url = {}

        existing_organization = self.organization_repository.get_organization(org_id)
        if existing_organization:
            existing_assets_hash = existing_organization["assets_hash"]
            existing_assets_url = existing_organization["assets_url"]
        new_assets_url_mapping = self._comapre_assets_and_push_to_s3(existing_assets_hash, new_assets_hash,
                                                                     existing_assets_url, org_id,
                                                                     "")
        return new_assets_url_mapping

    def on_event(self, event):
        logger.info(f"processing org event {event}")
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'node_modules', 'singularitynet-platform-contracts'))
        registry_contract = self.blockchain_util.get_contract_instance(base_contract_path, "REGISTRY", net_id)
        event_org_data = event['data']['json_str']
        org_id_bytes = event_org_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\\x00")

        blockchain_org_data = registry_contract.functions.getOrganizationById(org_id.encode('utf-8')).call()
        org_metadata_uri = Web3.toText(blockchain_org_data[2])[7:].rstrip("\u0000")
        ipfs_data = self.ipfs_util.read_file_from_ipfs(org_metadata_uri)

        if event['name'] == "OrganizationCreated" or event['name'] == 'OrganizationModified':
            self.process_organization_create_update_event(org_id, blockchain_org_data, ipfs_data, org_metadata_uri)
        elif event['name'] == "OrganizationDeleted":
            self.process_organization_delete_event(org_id)

    def process_organization_create_update_event(self, org_id, org_data, ipfs_org_metadata, org_metadata_uri):

        try:
            if (org_data is not None and org_data[0]):
                self.organization_repository.begin_transaction()

                new_assets_hash = ipfs_org_metadata['assets']
                new_assets_url_mapping = self._get_new_assets_url(org_id, ipfs_org_metadata)
                description = ipfs_org_metadata['description']

                self.organization_repository.create_or_updatet_organization(
                    org_id=org_id, org_name=ipfs_org_metadata["org_name"], owner_address=org_data[3],
                    org_metadata_uri=org_metadata_uri, description=description, assets_hash=new_assets_hash,
                    assets_url=new_assets_url_mapping)
                self.organization_repository.delete_organization_groups(org_id=org_id)
                self.organization_repository.create_organization_groups(
                    org_id=org_id, groups=ipfs_org_metadata["groups"])
                self.organization_repository.del_members(org_id=org_id)
                # self.organization_dao.create_or_update_members(org_id, org_data[4])
                self.organization_repository.commit_transaction()

        except Exception as e:
            self.organization_repository.rollback_transaction()
            raise e

    def process_organization_delete_event(self, org_id):
        try:
            self.connection.begin_transaction()
            self.organization_repository.delete_organization(org_id=org_id)
            self.organization_repository.delete_organization_groups(org_id=org_id)
            services = self.service_repository.get_services(org_id=org_id)
            for service in services:
                self.service_repository.delete_service(
                    org_id=org_id, service_id=service['service_id'])

            self.connection.commit_transaction()


        except Exception as e:
            print(e)
            self.connection.rollback_transaction()
            raise e
