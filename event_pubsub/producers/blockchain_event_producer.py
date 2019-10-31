import os

import web3
from web3 import Web3

from common.blockchain_util import BlockChainUtil
from event_pubsub.event_repository import EventRepository
from event_pubsub.producers.event_producer import EventProducer
from event_pubsub.repository import Repository


class BlockchainEventProducer(EventProducer):
    def __init__(self, ws_provider, repository=None, ):
        self.web3 = Web3(web3.providers.WebsocketProvider(ws_provider))
        self.blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self.event_repository=repository

    def get_events_from_blockchain(self, start_block_number, end_block_number, net_id):

        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'node_modules', 'singularitynet-platform-contracts'))

        contract = self.blockchain_util.get_contract_instance(base_contract_path, "MPE", net_id=net_id)
        contract_events = contract.events
        all_blockchain_events = []

        for attributes in contract_events.abi:
            if attributes['type'] == 'event':
                event_name = attributes['name']
                event_object = getattr(contract.events, event_name)
                blockchain_events = event_object.createFilter(fromBlock=start_block_number,
                                                              toBlock=end_block_number).get_all_entries()
                all_blockchain_events.extend(blockchain_events)

        return all_blockchain_events

    def produce_contract_events(self, start_block_number, end_block_number, net_id):

        events = self.get_events_from_blockchain(start_block_number, end_block_number, net_id)
        print("read events count" + str(len(events)))
        return events


class RegistryEventProducer(BlockchainEventProducer):
    REGISTRY_EVENT_READ_BATCH_LIMIT = 500000

    def __init__(self, ws_provider, repository=None):
        super().__init__(ws_provider, repository)
        self.contract_name = "REGISTRY"

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

        self.event_repository.insert_registry_event(block_number, event_name, json_str, processed, transaction_hash,
                                                    log_index,
                                                    error_code, error_message)

    def push_events_to_repository(self, events):
        for event in events:
            self.push_event(event)

    def get_end_block_number(self, last_processed_block_number):
        current_block_number = self.blockchain_util.get_current_block_no()
        end_block_number = last_processed_block_number + self.REGISTRY_EVENT_READ_BATCH_LIMIT
        if current_block_number <= end_block_number:
            end_block_number = current_block_number

        return end_block_number

    def produce_event(self, net_id):
        last_block_number = self.event_repository.read_last_read_block_number_for_event("REGISTRY")
        end_block_number = self.get_end_block_number(last_block_number)

        events = self.produce_contract_events(last_block_number, end_block_number, net_id)
        self.push_events_to_repository(events)
        self.event_repository.update_last_read_block_number_for_event("REGISTRY", end_block_number)

        return events


class MPEEventProducer(BlockchainEventProducer):
    MPE_EVENT_READ_BATCH_LIMIT = 50000

    def __init__(self, ws_provider, repository=None):
        super().__init__(ws_provider, repository)

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

        self.event_repository.insert_mpe_event(block_number, event_name, json_str, processed, transaction_hash,
                                               log_index,
                                               error_code, error_message)

    def push_events_to_repository(self, events):
        for event in events:
            self.push_event(event)

    def get_end_block_number(self, last_processed_block_number):
        current_block_number = self.blockchain_util.get_current_block_no()
        end_block_number = last_processed_block_number + self.MPE_EVENT_READ_BATCH_LIMIT
        if current_block_number <= end_block_number:
            end_block_number = current_block_number

        return end_block_number

    def produce_event(self, net_id):
        last_block_number = self.event_repository.read_last_read_block_number_for_event("MPE")
        end_block_number = self.get_end_block_number(last_block_number)

        events = self.produce_contract_events(last_block_number, end_block_number, net_id)
        self.push_events_to_repository(events)
        self.event_repository.update_last_read_block_number_for_event("MPE", end_block_number)
        return events


if __name__ == "__main__":


    try:
        blockchain_event_producer = MPEEventProducer("wss://ropsten.infura.io/ws")
        blockchain_event_producer.produce_event(3)
    except Exception as e:
        raise e
