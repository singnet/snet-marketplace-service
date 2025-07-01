import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock
from unittest.mock import patch

from contract_api.application.consumers.mpe_event_consumer import MPEEventConsumer
from contract_api.infrastructure.repositories.channel_repository import ChannelRepository
from contract_api.application.handlers.consumer_handlers import mpe_event_consumer


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        self.channel_repository = ChannelRepository()

    def tearDown(self):
        self.channel_repository.delete_channel(23)

    def test_on_event_channel_open(self):
        event = {'Records': [
            {'body': '{\n "Message" : "{\\"blockchain_name\\": \\"Ethereum\\", \\"blockchain_event\\": {\\"name\\": \\"ChannelOpen\\", \\"data\\": {\\"block_no\\": 8626046, \\"from_address\\": \\"0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF\\", \\"to_address\\": \\"0x03e7D37A13ed807B2311418095E23fA8Ff9DE380\\", \\"json_str\\": \\"{\'sender\': \'0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF\', \'recipient\': \'0x4DD0668f583c92b006A81743c9704Bd40c876fDE\', \'groupId\': b\\\\\\"5\'\\\\\\\\xff\\\\\\\\xdb\\\\\\\\xcf\\\\\\\\xff2l\\\\\\\\x0c\\\\\\\\xfaKp\\\\\\\\xafX\\\\\\\\x0e\\\\\\\\xd2\\\\\\\\xf5E\\\\\\\\xa1j\\\\\\\\xafr\\\\\\\\xd0\\\\\\\\x13\\\\\\\\xf9\\\\\\\\t(\\\\\\\\xdaS\\\\\\\\xb7_:\\\\\\", \'channelId\': 23, \'nonce\': 0, \'signer\': \'0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF\', \'amount\': 1, \'expiration\': 10768765}\\", \\"transaction_hash\\": \\"0xe2d933987f97b20145071f1ff61e9cb74233a903a696c7cd468bc56bf609d96d\\", \\"log_index\\": 12}}}"\n }'}
        ]}

        mpe_event_consumer(event, context = None)

        channel_result = self.channel_repository.get_channel(23)
        assert channel_result is not None

        assert channel_result.channel_id == 23
        assert channel_result.sender == '0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF'
        assert channel_result.recipient == '0x4DD0668f583c92b006A81743c9704Bd40c876fDE'
        assert channel_result.group_id == 'NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko2lO3Xzo='
        assert channel_result.balance_in_cogs == 1
        assert channel_result.pending == 0
        assert channel_result.nonce == 0
        assert channel_result.expiration == 10768765
        assert channel_result.signer == '0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF'

    @patch("common.blockchain_util.BlockChainUtil.get_contract_instance")
    def test_on_event_channels_add_funds(self, mock_get_contract_instance):
        create_event = {'Records': [
            {'body': '{\n "Message" : "{\\"blockchain_name\\": \\"Ethereum\\", \\"blockchain_event\\": {\\"name\\": \\"ChannelOpen\\", \\"data\\": {\\"block_no\\": 8626046, \\"from_address\\": \\"0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF\\", \\"to_address\\": \\"0x03e7D37A13ed807B2311418095E23fA8Ff9DE380\\", \\"json_str\\": \\"{\'sender\': \'0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF\', \'recipient\': \'0x4DD0668f583c92b006A81743c9704Bd40c876fDE\', \'groupId\': b\\\\\\"5\'\\\\\\\\xff\\\\\\\\xdb\\\\\\\\xcf\\\\\\\\xff2l\\\\\\\\x0c\\\\\\\\xfaKp\\\\\\\\xafX\\\\\\\\x0e\\\\\\\\xd2\\\\\\\\xf5E\\\\\\\\xa1j\\\\\\\\xafr\\\\\\\\xd0\\\\\\\\x13\\\\\\\\xf9\\\\\\\\t(\\\\\\\\xdaS\\\\\\\\xb7_:\\\\\\", \'channelId\': 23, \'nonce\': 0, \'signer\': \'0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF\', \'amount\': 1, \'expiration\': 10768765}\\", \\"transaction_hash\\": \\"0xe2d933987f97b20145071f1ff61e9cb74233a903a696c7cd468bc56bf609d96d\\", \\"log_index\\": 12}}}"\n }'}
        ]}

        mpe_event_consumer(create_event, context = None)

        update_event = {'Records': [
            {'body': '{\n "Message" : "{\\"blockchain_name\\": \\"Ethereum\\", \\"blockchain_event\\": {\\"name\\": \\"ChannelAddFunds\\", \\"data\\": {\\"block_no\\": 8626046, \\"from_address\\": \\"0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF\\", \\"to_address\\": \\"0x03e7D37A13ed807B2311418095E23fA8Ff9DE380\\", \\"json_str\\": \\"{\'channelId\': 23, \'additionalFunds\': 10}\\", \\"transaction_hash\\": \\"0xe2d933987f97b20145071f1ff61e9cb74233a903a696c7cd468bc56bf609d96d\\", \\"log_index\\": 12}}}"\n }'}
        ]}

        block_chain_channel_data = [0, '0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF',
                                    '0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF',
                                    '0x4DD0668f583c92b006A81743c9704Bd40c876fDE',
                                    b"5'\xff\xdb\xcf\xff2l\x0c\xfaKp\xafX\x0e\xd2\xf5E\xa1j\xafr\xd0\x13\xf9\t(\xdaS\xb7_:",
                                    11, 10768765]

        mock_get_contract_instance.return_value = Mock(
            functions = Mock(
                channels = Mock(
                    return_value = Mock(
                        call = Mock(return_value = block_chain_channel_data)
                    )
                )
            )
        )

        mpe_event_consumer(update_event, context = None)

        channel_result = self.channel_repository.get_channel(23)
        assert channel_result.sender == '0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF'
        assert channel_result.recipient == '0x4DD0668f583c92b006A81743c9704Bd40c876fDE'
        assert channel_result.group_id == 'NSf/28//MmwM+ktwr1gO0vVFoWqvctAT+Qko2lO3Xzo='
        assert channel_result.balance_in_cogs == 11
        assert channel_result.pending == 0
        assert channel_result.nonce == 0
        assert channel_result.expiration == 10768765
        assert channel_result.signer == '0x6E7BaCcc00D69eab748eDf661D831cd2c7f3A4DF'

