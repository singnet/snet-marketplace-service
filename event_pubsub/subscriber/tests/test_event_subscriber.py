import unittest


class TestBlockchainEventSubsriber(unittest.TestCase):
    def setUp(self):
        pass

    #
    # @patch('common.blockchain_util.BlockChainUtil.get_contract_instance')
    # @patch('event_pubsub.event_repository.EventRepository.read_last_read_block_number_for_event')
    # def test_produce_registry_events_from_blockchain(self, mock_last_block_number, mock_get_contract_instance):
    #     registry_event_producer = RegistryEventProducer("wss://ropsten.infura.io/ws", "REGISTRY")
    #
    #     org_created_event_object = Mock()
    #     org_created_event_object.createFilter = Mock(
    #         return_value=Mock(get_all_entries=Mock(return_value=[AttributeDict({'args': AttributeDict({
    #             'orgId': b'snet\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'}),
    #             'event': 'OrganizationCreated', 'logIndex': 1, 'transactionIndex': 15,
    #             'transactionHash': HexBytes(
    #                 '0x7934a42442792f6d5a171df218b66161021c885085187719c991ec58d7459821'),
    #             'address': '0x663422c6999Ff94933DBCb388623952CF2407F6f',
    #             'blockHash': HexBytes('0x1da77d63b7d57e0a667ffb9f6d23be92f3ffb5f4b27b39b86c5d75bb167d6779'),
    #             'blockNumber': 6243627})])))
    #
    #     mock_get_contract_instance.return_value = Mock(
    #         events=Mock(organizationCreated=org_created_event_object,
    #                     abi=[{"type": "event", "name": "organizationCreated"}]))
    #
    #     mock_last_block_number.return_value = 0
    #
    #     blockchain_events = registry_event_producer.produce_event(3)

    def test_event_subscriber(self):
        pass

    def test_push_events(self):
        pass


if __name__ == "__main__":
    unittest.main()
