from enum import Enum

import web3
from web3 import Web3

from event_pubsub.producers.event_producer import EventProducer
import json
from datetime import datetime

from event_pubsub.repository import Repository


class ContractType(Enum):
    REGISTRY = "REGISTRY"
    MPE = "MPE"


class BlockchainEventProducer(EventProducer):

    def __init__(self, ws_provider, repository=None):
        self.web3 = Web3(web3.providers.WebsocketProvider(ws_provider))
        self.repository = Repository(NETWORKS={
            'db': {"HOST": "localhost",
                   "USER": "root",
                   "PASSWORD": "password",
                   "NAME": "pub_sub",
                   "PORT": 3306,
                   }
        })

    def get_contract_details(self, contract_name, base_path, net_id):

        if contract_name == "REGISTRY":
            json_file = "Registry.json"
        elif contract_name == "MPE":
            json_file = "MultiPartyEscrow.json"
        else:
            raise Exception("Invalid contract Type {}".format(contract_name))

        contract_network_path = base_path + "{}/{}".format("networks", json_file)
        contract_abi_path = base_path + "{}/{}".format("abi", json_file)

        with open(contract_abi_path) as abi_file:
            abi_value = json.load(abi_file)
            contract_abi = abi_value

        with open(contract_network_path) as network_file:
            network_value = json.load(network_file)
            contract_address = network_value[str(net_id)]['address']

        return contract_abi, contract_address

    def get_events_from_blockchain(self, start_block_number, end_block_number, contract_abi, contract_address):

        contract = self.web3.eth.contract(address=self.web3.toChecksumAddress(contract_address), abi=contract_abi)
        contract_events = contract.events
        all_blockchain_events = []

        for attributes in contract_events.abi:
            if attributes['type'] == 'event':
                event_name = attributes['name']
                event_object = getattr(contract.events, event_name)
                blockchain_events = event_object.createFilter(fromBlock=start_block_number,
                                                              toBlock='latest').get_all_entries()
                all_blockchain_events.extend(blockchain_events)

        return all_blockchain_events

    def push_event(self, event):
        """
          `row_id` int(11) NOT NULL AUTO_INCREMENT,
          `block_no` int(11) NOT NULL,
          `event` varchar(256) NOT NULL,
          `json_str` text,
          `processed` bit(1) DEFAULT NULL,
          `transactionHash` varchar(256) DEFAULT NULL,
          `logIndex` varchar(256) DEFAULT NULL,
          `error_code` int(11) DEFAULT NULL,
          `error_msg` varchar(256) DEFAULT NULL,
          `row_updated` timestamp NULL DEFAULT NULL,
          `row_created` timestamp NULL DEFAULT NULL,
        :param event:
        :return:
        """

        block_number = event.blockNumber
        event_name = event.event
        json_str = str(dict(event.args))
        processed = 0
        transaction_hash = str(event.transactionHash)
        log_index = event.logIndex
        error_code = 0
        error_message = ""

        # insert into database here
        insert_query = "Insert into registry_events_raw (block_no, event, json_str, processed, transactionHash, logIndex ,error_code,error_msg,row_updated,row_created) " \
                       "VALUES ( %s, %s, %s, %s, %s , %s, %s, %s, %s, %s ) "
        insert_params = [block_number, event_name, json_str, 0, transaction_hash, log_index, error_code, error_message,
                         datetime.utcnow(), datetime.utcnow()]

        query_reponse = self.repository.execute(insert_query, insert_params)

    def produce_contract_events(self, start_block_number, end_block_number, contract_name, net_id):
        contract_abi, contract_address = self.get_contract_details(contract_name,
                                                                   "../node_modules/singularitynet-platform-contracts/",
                                                                   net_id)
        events = self.get_events_from_blockchain(start_block_number, end_block_number, contract_abi, contract_address)

        for event in events:
            self.push_event(event)

    def produce_all_events(self):
        start_block_number = 6629000
        end_block_number = 6629468
        net_id = 3

        #self.produce_contract_events(start_block_number, end_block_number, "REGISTRY", net_id)
        self.produce_contract_events(start_block_number, end_block_number, "MPE", net_id)


if __name__ == "__main__":
    """
        abiMPE = JSON.parse(mpe_str),
        mpeAddr = JSON.parse(addr_str),
        contractAddrForMPE = mpeAddr[netId].address;
    
    """
    try:
        blockchain_event_producer = BlockchainEventProducer("wss://ropsten.infura.io/ws")
        blockchain_event_producer.produce_all_events()
    except Exception as e:
        raise e
