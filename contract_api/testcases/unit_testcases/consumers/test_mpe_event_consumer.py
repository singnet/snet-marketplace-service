import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock
from unittest.mock import patch

from common.repository import Repository
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.consumers.mpe_event_consumer import MPEEventConsumer
from contract_api.dao.mpe_repository import MPERepository


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass

    @patch("common.blockchain_util.BlockChainUtil.get_contract_instance")
    def test_on_event_channel_open(self, mock_get_contract_instance):
        event = {"blockchain_event": {"data": {'row_id': 347, 'block_no': 6629145, 'event': 'ChannelOpen',
                           'json_str': '{\'sender\': \'0x669CCF5025C08304Fd836d7A136634E22C5Dd31C\', \'recipient\': \'0xaceB1EaCA36061ff29Ddb7c963142abbFf23e508\', \'groupId\': b"\\xbc\\xb0\\xa1\\x93Z\\xa1\\xab\\x11\\xfd\\xbcX\\x1c\\x1cxZ\\xdc.\\xb6\\xba\\x8e\\xc6\\xc8C*\\xd7\\xa9\\xea\\x91\\xe6\'\\xae\\xfc", \'channelId\': 143, \'nonce\': 0, \'signer\': \'0x669CCF5025C08304Fd836d7A136634E22C5Dd31C\', \'amount\': 1, \'expiration\': 8731644}',
                           'processed': b'\x00',
                           'transactionHash': "b'\\xb7X\\xde\\x13{\\x13\\x05$\\x99\\x8c\\x1a\\xe4\\xae\\xdf\\x0f\\x88\\x08\\xd4\\x0f\\x7fVV^T;s\\x93\\x90$?\\xe6\\x14'",
                           'logIndex': '42', 'error_code': 1, 'error_msg': '',
                           'row_updated': datetime(2019, 10, 23, 12, 35, 53),
                           'row_created': datetime(2019, 10, 23, 12, 35, 53)}, "name": "ChannelOpen"}}

        block_chain_channel_data = [0, '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C',
                                    '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C',
                                    '0xaceB1EaCA36061ff29Ddb7c963142abbFf23e508',
                                    b"\xbc\xb0\xa1\x93Z\xa1\xab\x11\xfd\xbcX\x1c\x1cxZ\xdc.\xb6\xba\x8e\xc6\xc8C*\xd7\xa9\xea\x91\xe6'\xae\xfc",
                                    100, 8731699]
        mock_get_contract_instance.return_value = Mock(
            functions = Mock(
                channels = Mock(return_value = Mock(call = Mock(return_value = block_chain_channel_data)))))

        mpe_event_consumer = MPEEventConsumer("wss://ropsten.infura.io/ws")
        mpe_repository = MPERepository(Repository(NETWORK_ID, NETWORKS=NETWORKS))
        mpe_repository.delete_mpe_channel(143)
        mpe_event_consumer.on_event(event=event)

        channel_result = mpe_repository.get_mpe_channels(143)
        assert channel_result[0]['channel_id'] == 143
        assert channel_result[0]['sender'] == '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C'
        assert channel_result[0]['recipient'] == '0xaceB1EaCA36061ff29Ddb7c963142abbFf23e508'
        assert channel_result[0]['groupId'] == 'vLChk1qhqxH9vFgcHHha3C62uo7GyEMq16nqkeYnrvw='
        assert channel_result[0]['balance_in_cogs'] == Decimal('1.00000000')
        assert channel_result[0]['pending'] == Decimal('0E-8')
        assert channel_result[0]['expiration'] == 8731644
        assert channel_result[0]['signer'] == '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C'
        # assert str(channel_result[0]['row_created']) == '2019-10-23 13:37:09'
        # assert str(channel_result[0]['row_updated']) == '2019-10-30 06:52:18'

    @patch("common.blockchain_util.BlockChainUtil.get_contract_instance")
    def test_on_event_channels_add_funds(self, mock_get_contract_instance):
        create_event = {"blockchain_event": {"data": {'row_id': 347, 'block_no': 6629145, 'event': 'ChannelOpen',
                                  'json_str': '{\'sender\': \'0x669CCF5025C08304Fd836d7A136634E22C5Dd31C\', \'recipient\': \'0xaceB1EaCA36061ff29Ddb7c963142abbFf23e508\', \'groupId\': b"\\xbc\\xb0\\xa1\\x93Z\\xa1\\xab\\x11\\xfd\\xbcX\\x1c\\x1cxZ\\xdc.\\xb6\\xba\\x8e\\xc6\\xc8C*\\xd7\\xa9\\xea\\x91\\xe6\'\\xae\\xfc", \'channelId\': 143, \'nonce\': 0, \'signer\': \'0x669CCF5025C08304Fd836d7A136634E22C5Dd31C\', \'amount\': 1, \'expiration\': 8731644}',
                                  'processed': b'\x00',
                                  'transactionHash': "b'\\xb7X\\xde\\x13{\\x13\\x05$\\x99\\x8c\\x1a\\xe4\\xae\\xdf\\x0f\\x88\\x08\\xd4\\x0f\\x7fVV^T;s\\x93\\x90$?\\xe6\\x14'",
                                  'logIndex': '42', 'error_code': 1, 'error_msg': '',
                                  'row_updated': datetime(2019, 10, 23, 12, 35, 53),
                                  'row_created': datetime(2019, 10, 23, 12, 35, 53)}, "name": "ChannelOpen"}}
        mpe_event_consumer = MPEEventConsumer("wss://ropsten.infura.io/ws")

        mpe_repository = MPERepository(Repository(NETWORK_ID, NETWORKS=NETWORKS))
        mpe_repository.delete_mpe_channel(143)

        mpe_event_consumer.on_event(event=create_event)

        update_event = {"blockchain_event": {"data": {'row_id': 349, 'block_no': 6629307, 'event': 'ChannelAddFunds',
                                  'json_str': "{'channelId': 143, 'additionalFunds': 10}", 'processed': b'\x00',
                                  'transactionHash': "b'\\x14\\xb3\\x8b\\x18\\xf1@6\\xe7\\x85T\\x82\\xf3\\xe7\\x15\\x82U\\xd8(\\x0f\\xe8T\\xac\\xdb\\xbdg\\xad0s\\xb6\\xd8\\x03\\x98'",
                                  'logIndex': '4', 'error_code': 1, 'error_msg': '',
                                  'row_updated': datetime(2019, 10, 23, 12, 35, 53),
                                  'row_created': datetime(2019, 10, 23, 12, 35, 53)}, "name": "ChannelAddFunds"}}

        block_chain_channel_data = [0, '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C',
                                    '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C',
                                    '0xaceB1EaCA36061ff29Ddb7c963142abbFf23e508',
                                    b"\xbc\xb0\xa1\x93Z\xa1\xab\x11\xfd\xbcX\x1c\x1cxZ\xdc.\xb6\xba\x8e\xc6\xc8C*\xd7\xa9\xea\x91\xe6'\xae\xfc",
                                    100, 8731699]

        mock_get_contract_instance.return_value = Mock(
            functions=Mock(channels=Mock(return_value=Mock(call=Mock(return_value=block_chain_channel_data)))))

        mpe_event_consumer.on_event(event=update_event)

        channel_result = mpe_repository.get_mpe_channels(143)
        assert channel_result[0]['channel_id'] == 143
        assert channel_result[0]['sender'] == '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C'
        assert channel_result[0]['recipient'] == '0xaceB1EaCA36061ff29Ddb7c963142abbFf23e508'
        assert channel_result[0]['groupId'] == 'vLChk1qhqxH9vFgcHHha3C62uo7GyEMq16nqkeYnrvw='
        assert channel_result[0]['balance_in_cogs'] == Decimal('100.00000000')
        assert channel_result[0]['pending'] == Decimal('0E-8')
        assert channel_result[0]['expiration'] == 8731699
        assert channel_result[0]['signer'] == '0x669CCF5025C08304Fd836d7A136634E22C5Dd31C'
        # assert str(channel_result[0]['row_created']) == '2019-10-23 13:37:09'