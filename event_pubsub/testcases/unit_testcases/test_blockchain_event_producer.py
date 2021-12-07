import unittest
from unittest.mock import Mock, patch

from hexbytes import HexBytes
from web3.datastructures import AttributeDict

from event_pubsub.config import NETWORKS
from event_pubsub.event_repository import EventRepository
from event_pubsub.producers.blockchain_event_producer import MPEEventProducer, RegistryEventProducer, \
    AirdropEventProducer
from event_pubsub.repository import Repository

infura_endpoint = "https://ropsten.infura.io/"

class TestBlockchainEventProducer(unittest.TestCase):
    def setUp(self):
        pass

    @patch('common.blockchain_util.BlockChainUtil.get_contract_instance')
    @patch('event_pubsub.event_repository.EventRepository.read_last_read_block_number_for_event')
    @patch('common.blockchain_util.BlockChainUtil.get_current_block_no')
    def test_produce_registry_events_from_blockchain(self, mock_get_current_block_no, mock_last_block_number,
                                                     mock_get_contract_instance):
        registry_event_producer = RegistryEventProducer(infura_endpoint, Repository(NETWORKS))

        org_created_event_object = Mock()
        event_repository = EventRepository(Repository(NETWORKS))
        org_created_event_object.createFilter = Mock(
            return_value=Mock(get_all_entries=Mock(return_value=[AttributeDict({'args': AttributeDict({
                'orgId': b'snet\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'}),
                'event': 'OrganizationCreated', 'logIndex': 1, 'transactionIndex': 15,
                'transactionHash': HexBytes(
                    '0x7934a42442792f6d5a171df218b66161021c885085187719c991ec58d7459821'),
                'address': '0x663422c6999Ff94933DBCb388623952CF2407F6f',
                'blockHash': HexBytes('0x1da77d63b7d57e0a667ffb9f6d23be92f3ffb5f4b27b39b86c5d75bb167d6779'),
                'blockNumber': 6243627})])))

        mock_get_contract_instance.return_value = Mock(
            events=Mock(organizationCreated=org_created_event_object,
                        abi=[{"type": "event", "name": "organizationCreated"}]))

        mock_last_block_number.return_value = 50
        mock_get_current_block_no.return_value = 50

        blockchain_events = registry_event_producer.produce_event(3)
        assert blockchain_events == [AttributeDict({'args': AttributeDict({
            'orgId': b'snet\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'}),
            'event': 'OrganizationCreated', 'logIndex': 1,
            'transactionIndex': 15, 'transactionHash': HexBytes(
                '0x7934a42442792f6d5a171df218b66161021c885085187719c991ec58d7459821'),
            'address': '0x663422c6999Ff94933DBCb388623952CF2407F6f',
            'blockHash': HexBytes(
                '0x1da77d63b7d57e0a667ffb9f6d23be92f3ffb5f4b27b39b86c5d75bb167d6779'),
            'blockNumber': 6243627})]

    @patch('common.blockchain_util.BlockChainUtil.get_contract_instance')
    @patch('event_pubsub.event_repository.EventRepository.read_last_read_block_number_for_event')
    @patch('common.blockchain_util.BlockChainUtil.get_current_block_no')
    def test_produce_mpe_events_from_blockchain(self, mock_get_current_block_no, mock_last_block_number,
                                                mock_get_contract_instance):
        mpe_event_producer = MPEEventProducer(infura_endpoint, Repository(NETWORKS))
        event_repository = EventRepository(Repository(NETWORKS))

        deposit_fund_Event_object = Mock()
        deposit_fund_Event_object.createFilter = Mock(
            return_value=Mock(get_all_entries=Mock(return_value=[AttributeDict(
                {'args': AttributeDict({'sender': '0xabd2cCb3828b4428bBde6C2031A865b0fb272a5A', 'amount': 30000000}),
                 'event': 'DepositFunds', 'logIndex': 1, 'transactionIndex': 18,
                 'transactionHash': HexBytes('0x562cc2fa59d9c7a4aa56106a19ad9c8078a95ae68416619fc191d86c50c91f12'),
                 'address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C',
                 'blockHash': HexBytes('0xe06042a4d471351c0ee9e50056bd4fb6a0e158b2489ba70775d3c06bd29da19b'),
                 'blockNumber': 6286405})])))
        mock_last_block_number.return_value = 50
        mock_get_current_block_no.return_value = 50

        # Testing contract events
        mock_get_contract_instance.return_value = Mock(
            events=Mock(DepositFunds=deposit_fund_Event_object,
                        abi=[{"type": "event", "name": "DepositFunds"}]))
        blockchain_events = mpe_event_producer.produce_event(3)
        assert blockchain_events == [AttributeDict(
            {'args': AttributeDict({'sender': '0xabd2cCb3828b4428bBde6C2031A865b0fb272a5A', 'amount': 30000000}),
             'event': 'DepositFunds', 'logIndex': 1, 'transactionIndex': 18,
             'transactionHash': HexBytes('0x562cc2fa59d9c7a4aa56106a19ad9c8078a95ae68416619fc191d86c50c91f12'),
             'address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C',
             'blockHash': HexBytes('0xe06042a4d471351c0ee9e50056bd4fb6a0e158b2489ba70775d3c06bd29da19b'),
             'blockNumber': 6286405})]

        # Testing Airdrop events
        airdrop_event_producer = AirdropEventProducer(infura_endpoint, Repository(NETWORKS))
        blockchain_events = airdrop_event_producer.produce_event(3)
        assert blockchain_events == [AttributeDict(
            {'args': AttributeDict({'sender': '0xabd2cCb3828b4428bBde6C2031A865b0fb272a5A', 'amount': 30000000}),
             'event': 'DepositFunds', 'logIndex': 1, 'transactionIndex': 18,
             'transactionHash': HexBytes('0x562cc2fa59d9c7a4aa56106a19ad9c8078a95ae68416619fc191d86c50c91f12'),
             'address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C',
             'blockHash': HexBytes('0xe06042a4d471351c0ee9e50056bd4fb6a0e158b2489ba70775d3c06bd29da19b'),
             'blockNumber': 6286405})]
