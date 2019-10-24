import json
import unittest
from unittest.mock import patch, Mock

from hexbytes import HexBytes
from web3.datastructures import AttributeDict

from event_pubsub.producers.blockchain_event_producer import BlockchainEventProducer


class TestBlockchainEventProducer(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_contract_details(self):
        blockchain_event_producer = BlockchainEventProducer("wss://ropsten.infura.io/ws")

        abi, address = blockchain_event_producer.get_contract_details("REGISTRY",
                                                                      "../node_modules/singularitynet-platform-contracts/",
                                                                      3)


        blockchain_events = blockchain_event_producer.get_events_from_blockchain(0, 6243627, abi,
                                                                                 address)

        assert address == "0x663422c6999ff94933dbcb388623952cf2407f6f"
        assert abi[0]['name'] == 'OrganizationCreated'

    # def test_get_events_from_blockchain(self):
    #     blockchain_event_producer = BlockchainEventProducer("wss://ropsten.infura.io/ws")
    #     contract_abi = ""
    #     contract_address = "0x663422c6999ff94933dbcb388623952cf2407f6f"
    #
    #     org_created_event_object = Mock()
    #     org_created_event_object.createFilter = Mock(
    #         return_value=Mock(get_all_entries=Mock(return_value={'args': AttributeDict({
    #             'orgId': b'snet\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'}),
    #             'event': 'OrganizationCreated', 'logIndex': 1, 'transactionIndex': 15,
    #             'transactionHash': HexBytes(
    #                 '0x7934a42442792f6d5a171df218b66161021c885085187719c991ec58d7459821'),
    #             'address': '0x663422c6999Ff94933DBCb388623952CF2407F6f',
    #             'blockHash': HexBytes('0x1da77d63b7d57e0a667ffb9f6d23be92f3ffb5f4b27b39b86c5d75bb167d6779'),
    #             'blockNumber': 6243627})))
    #
    #     blockchain_event_producer.web3.eth.contract = Mock(return_value=Mock(
    #         events=Mock(organizationCreated=org_created_event_object,
    #                     abi=[{"type": "event", "name": "organizationCreated"}])))
    #
    #     blockchain_events = blockchain_event_producer.get_events_from_blockchain(0, 6243627, contract_abi,
    #                                                                              contract_address)
    #
    #     assert blockchain_events[
    #                'args'].orgId == b'snet\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    #     assert blockchain_events['event'] == 'OrganizationCreated'


    def test_push_events(self):
        pass



if __name__ == "__main__":
    unittest.main()
