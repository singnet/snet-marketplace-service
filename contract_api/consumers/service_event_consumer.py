import web3
from ssh.util import get_logger
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from contract_api.config import ASSETS_PREFIX, ASSETS_BUCKET_NAME

from contract_api.dao.service_repository import ServiceRepository

from contract_api.config import NETWORK_ID, NETWORKS
from common.repository import Repository
import json
import os

logger = get_logger(__name__)


class ServiceEventConsumer(object):
    connection = Repository(NETWORK_ID, NETWORKS=NETWORKS)
    service_repository = ServiceRepository(connection)

    def __init__(self, ws_provider, ipfs_url, ipfs_port):
        self.ipfs_client = IPFSUtil(ipfs_url, ipfs_port)
        self.blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)

    def fetch_tags(self, registry_contract, org_id_hex, service_id_hex):
        tags_data = registry_contract.functions.getServiceRegistrationById(
            org_id_hex, service_id_hex).call()
        return tags_data

    def on_event(self, event):
        logger.info(f"processing service event {event}")
        event_data = event['data']
        event_name = event["name"]

        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'node_modules', 'singularitynet-platform-contracts'))
        registry_contract = self.blockchain_util.get_contract_instance(base_contract_path, "REGISTRY", net_id)

        service_data = eval(event_data['json_str'])

        org_id_bytes = service_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\x00")
        service_id_bytes = service_data['serviceId']
        service_id = Web3.toText(service_id_bytes).rstrip("\x00")

        tags_data = self.fetch_tags(
            registry_contract=registry_contract, org_id_hex=org_id.encode("utf-8"),
            service_id_hex=service_id.encode("utf-8"))

        if event_name in ['ServiceCreated', 'ServiceMetadataModified']:
            metadata_uri = Web3.toText(service_data['metadataURI'])[7:].rstrip("\u0000")
            service_ipfs_data = self.ipfs_client.read_file_from_ipfs(metadata_uri)
            self.process_service_data(org_id=org_id, service_id=service_id, new_ipfs_hash=metadata_uri,
                                      new_ipfs_data=service_ipfs_data, tags_data=tags_data)
        elif event_name == 'ServiceTagsModified':
            self.service_repository.update_tags(org_id=org_id, service_id=service_id,
                                                tags_data=self.fetch_tags(org_id_hex=org_id,
                                                                          service_id_hex=service_id))

        elif event_name == 'ServiceDeleted':
            self.service_repository.delete_service_dependents(org_id, service_id)
            self.service_repository.delete_service(
                org_id=org_id, service_id=service_id)

    def process_event(self):
        pass

    def _push_asset_to_s3_using_hash(self, hash, org_id, service_id):
        io_bytes = self.ipfs_utll.read_bytesio_from_ipfs(hash)
        filename = hash.split("/")[1]
        new_url = self.s3_util.push_io_bytes_to_s3(ASSETS_PREFIX + "/" + org_id + "/" + service_id + "/" + filename,
                                                   ASSETS_BUCKET_NAME,
                                                   io_bytes)
        return new_url

    def _comapre_assets_and_push_to_s3(self, existing_assets_hash, new_assets_hash, existing_assets_url, org_id,
                                       service_id):
        """

        :param existing_assets_hash: contains asset_type and its has value stored in ipfs
        :param new_assets_hash:  contains asset type and its updated hash value in ipfs
        :param existing_assets_url:  contains asset type and s3_url value for given asset_type
        :param org_id:
        :param service_id:
        :return: dict of asset_type and new_s3_url
        """
        # this function compare assets and deletes and update the new assets

        assets_url_mapping = {}

        if not existing_assets_hash:
            existing_assets_hash = {}
        if not existing_assets_url:
            existing_assets_url = {}
        if not new_assets_hash:
            new_assets_hash = {}

        for new_asset_type, new_asset_hash in new_assets_hash.items():

            if isinstance(new_asset_hash, list):
                # if this asset_type contains list of assets than remove all existing assetes from s3 and add all new assets to s3
                #
                new_urls_list = []

                # remove all existing assets if exits
                if new_asset_type in existing_assets_url:
                    for url in existing_assets_url[new_asset_type]:
                        self.s3_util.delete_file_from_s3(url)

                # add new files to s3 and update the url
                for hash in new_assets_hash[new_asset_type]:
                    new_urls_list.append(
                        self._push_asset_to_s3_using_hash(hash, org_id, service_id))

                assets_url_mapping[new_asset_type] = new_urls_list

            elif isinstance(new_asset_hash, str):
                # if this asset_type has single value
                if new_asset_type in existing_assets_hash and existing_assets_hash[new_asset_type] == new_asset_hash:
                    # file is not updated , add existing url
                    assets_url_mapping[new_asset_type] = existing_assets_url[new_asset_type]

                else:
                    if new_asset_type in existing_assets_url:
                        url_of_file_to_be_removed = existing_assets_url[new_asset_type]
                        self.s3_util.delete_file_from_s3(
                            url_of_file_to_be_removed)

                    hash_of_file_to_be_pushed_to_s3 = new_assets_hash[new_asset_type]

                    assets_url_mapping[new_asset_type] = self._push_asset_to_s3_using_hash(
                        hash_of_file_to_be_pushed_to_s3, org_id, service_id)

            else:
                print(
                    "unknown type assets for org_id %s  service_id %s", org_id, service_id)

        return assets_url_mapping

    def _get_new_assets_url(self, org_id, service_id, new_ipfs_data):
        new_assets_hash = new_ipfs_data.get('assets', {})
        existing_assets_hash = {}
        existing_assets_url = {}

        existing_service_metadata = self.service_repository.get_service_metadata(service_id, org_id)
        if existing_service_metadata:
            existing_assets_hash = existing_service_metadata["assets_hash"]
            existing_assets_url = existing_service_metadata["assets_url"]
        assets_url_mapping = self._comapre_assets_and_push_to_s3(existing_assets_hash, new_assets_hash,
                                                                 existing_assets_url, org_id,
                                                                 service_id)
        return assets_url_mapping

    def process_service_data(self, org_id, service_id, new_ipfs_hash, new_ipfs_data, tags_data):
        try:

            self.connection.begin_transaction()

            assets_url = self._get_new_assets_url(
                org_id, service_id, new_ipfs_data)

            self.service_repository.delete_service_dependents(
                org_id=org_id, service_id=service_id)
            service_data = self.service_repository.create_or_update_service(
                org_id=org_id, service_id=service_id, ipfs_hash=new_ipfs_hash)
            service_row_id = service_data['last_row_id']
            self.service_repository.create_or_update_service_metadata(service_row_id=service_row_id, org_id=org_id,
                                                                      service_id=service_id,
                                                                      ipfs_data=new_ipfs_data, assets_url=assets_url)
            groups = new_ipfs_data.get('groups', [])
            group_insert_count = 0
            for group in groups:
                service_group_data = self.service_repository.create_group(service_row_id=service_row_id, org_id=org_id,
                                                                          service_id=service_id,
                                                                          grp_data={
                                                                              'group_id': group['group_id'],
                                                                              'group_name': group['group_name'],
                                                                              'pricing': json.dumps(group['pricing'])
                                                                          })
                group_insert_count = group_insert_count + service_group_data[0]
                endpoints = group.get('endpoints', [])
                endpoint_insert_count = 0
                for endpoint in endpoints:
                    service_data = self.service_repository.create_endpoints(service_row_id=service_row_id,
                                                                            org_id=org_id,
                                                                            service_id=service_id,
                                                                            endpt_data={
                                                                                'endpoint': endpoint,
                                                                                'group_id': group['group_id'],
                                                                            })
                    endpoint_insert_count = endpoint_insert_count + service_data[0]

            if (tags_data is not None and tags_data[0]):
                tags = tags_data[3]
                for tag in tags:
                    tag = tag.decode('utf-8')
                    tag = tag.rstrip("\u0000")
                    self.service_repository.create_tags(service_row_id=service_row_id, org_id=org_id,
                                                        service_id=service_id,
                                                        tag_name=tag,
                                                        )
            self.connection.commit_transaction()

        except Exception as e:

            self.connection.rollback_transaction()
            raise e
