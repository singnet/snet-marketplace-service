import json
from web3 import Web3

import os

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from contract_api.dao.organization_repository import OrganizationRepository
from contract_api.dao.service_repository import ServiceRepository

from common.repository import Repository
from config import NETWORK_ID, NETWORKS


class OrganizationEventConsumer(object):
    connection = Repository(NETWORK_ID, NETWORKS=NETWORKS)
    organization_repository = OrganizationRepository(connection)
    service_repository = ServiceRepository(connection)

    def __init__(self, ws_provider, ipfs_url=None):
        self.ipfs_client = IPFSUtil(ipfs_url, 80)
        self.blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)

    def get_contract_file_paths(self, base_path, contract_name):
        if contract_name == "REGISTRY":
            json_file = "Registry.json"
        elif contract_name == "MPE":
            json_file = "MultiPartyEscrow.json"
        else:
            raise Exception("Invalid contract Type {}".format(contract_name))

        contract_network_path = base_path + "{}/{}".format("networks", json_file)
        contract_abi_path = base_path + "{}/{}".format("abi", json_file)

        return contract_abi_path, contract_network_path

    def get_contract_details(self, contract_abi_path, contract_network_path, net_id):

        with open(contract_abi_path) as abi_file:
            abi_value = json.load(abi_file)
            contract_abi = abi_value

        with open(contract_network_path) as network_file:
            network_value = json.load(network_file)
            contract_address = network_value[str(net_id)]['address']

        return contract_abi, contract_address

    def on_event(self, event):
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'node_modules', 'singularitynet-platform-contracts'))
        registry_contract = self.blockchain_util.get_contract_instance(base_contract_path, "REGISTRY", net_id)
        event_org_data = event['data']['json_str']
        org_id_bytes = event_org_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\\x00")

        blockchain_org_data = registry_contract.functions.getOrganizationById(org_id.encode('utf-8')).call()
        org_metadata_uri = Web3.toText(blockchain_org_data[2])[7:].rstrip("\u0000")
        ipfs_data = self.ipfs_client.read_file_from_ipfs(org_metadata_uri)

        if event['name'] == "OrganizationCreated":
            self.process_organization_create_update_event(org_id, blockchain_org_data, ipfs_data, org_metadata_uri)
        elif event['name'] == "OrganizationDeleted":
            self.process_organization_delete_event(org_id)

    def process_organization_create_update_event(self, org_id, org_data, ipfs_org_metadata, org_metadata_uri):

        try:
            if (org_data is not None and org_data[0]):
                self.organization_repository.begin_transaction()
                self.organization_repository.create_or_updatet_organization(
                    org_id=org_id, org_name=ipfs_org_metadata["org_name"], owner_address=org_data[3],
                    org_metadata_uri=org_metadata_uri)
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
