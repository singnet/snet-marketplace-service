import web3
import json
from web3 import Web3

from common.ipfs_util import IPFSUtil
from event_pubsub.consumers.marketplace_event_consumer.dao.organization_repository import OrganizationRepository
from event_pubsub.consumers.marketplace_event_consumer.dao.service_repository import  ServiceRepository
from event_pubsub.repository import Repository
from datetime import datetime


class OrganizationEventConsumer(object):
    connection = (Repository(NETWORKS={
        'db': {"HOST": "localhost",
               "USER": "root",
               "PASSWORD": "password",
               "NAME": "pub_sub",
               "PORT": 3306,
               }
    }))
    organization_dao = OrganizationRepository(connection)

    service_dao = ServiceRepository(connection)

    def __init__(self,ws_provider,ipfs_url=None):
        self.ipfs_client = IPFSUtil(ipfs_url, 80)
        self.web3 = Web3(web3.providers.WebsocketProvider(ws_provider))

    def get_contract_file_paths(self,base_path,contract_name):
        if contract_name == "REGISTRY":
            json_file = "Registry.json"
        elif contract_name == "MPE":
            json_file = "MultiPartyEscrow.json"
        else:
            raise Exception("Invalid contract Type {}".format(contract_name))

        contract_network_path = base_path + "{}/{}".format("networks", json_file)
        contract_abi_path = base_path + "{}/{}".format("abi",json_file)

        return contract_abi_path,contract_network_path

    def get_contract_details(self, contract_abi_path, contract_network_path, net_id):

        with open(contract_abi_path) as abi_file:
            abi_value = json.load(abi_file)
            contract_abi = abi_value

        with open(contract_network_path) as network_file:
            network_value = json.load(network_file)
            contract_address = network_value[str(net_id)]['address']

        return contract_abi, contract_address


    def porcess_event(self):
        pass

    def on_event(self, event):
        # event = {'args': AttributeDict({
        #     'orgId': b'snet\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'}),
        #     'event': 'OrganizationCreated', 'logIndex': 1, 'transactionIndex': 15,
        #     'transactionHash': HexBytes(
        #         '0x7934a42442792f6d5a171df218b66161021c885085187719c991ec58d7459821'),
        #     'address': '0x663422c6999Ff94933DBCb388623952CF2407F6f',
        #     'blockHash': HexBytes('0x1da77d63b7d57e0a667ffb9f6d23be92f3ffb5f4b27b39b86c5d75bb167d6779'),
        #     'blockNumber': 6243627}






        net_id = 3
        abi_pat,network_path=self.get_contract_file_paths("../../node_modules/singularitynet-platform-contracts/","REGISTRY")
        contract_abi,contract_address= self.get_contract_details(abi_pat,network_path ,net_id)
        registry_contract =  self.web3.eth.contract(address=self.web3.toChecksumAddress(contract_address), abi=contract_abi)
        event_org_data=event['data']['json_str']
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
                self.organization_dao.begin_transaction()
                self.organization_dao.create_or_updatet_organization(
                    org_id=org_id, org_name=ipfs_org_metadata["org_name"], owner_address=org_data[3],
                    org_metadata_uri=org_metadata_uri)
                self.organization_dao.delete_organization_groups(org_id=org_id)
                self.organization_dao.create_organization_groups(
                    org_id=org_id, groups=ipfs_org_metadata["groups"])
                self.organization_dao.del_members(org_id=org_id)
               # self.organization_dao.create_or_update_members(org_id, org_data[4])
                self.organization_dao.commit_transaction()

        except Exception as e:
            self.organization_dao.rollback_transaction()
            raise e

    def process_organization_delete_event(self, org_id):
        try:
            self.connection.begin_transaction()
            self.organization_dao.delete_organization(org_id=org_id)
            self.organization_dao.delete_organization_groups(org_id=org_id)
            services = self.service_dao.get_services(org_id=org_id)
            for service in services:
                self.service_dao.delete_service(
                    org_id=org_id, service_id=service['service_id'])

            self.connection.commit_transaction()


        except Exception as e:
            print(e)
            self.connection.rollback_transaction()
            raise e
