import json
import unittest
from datetime import datetime
from unittest.mock import patch, Mock

from hexbytes import HexBytes
from web3.datastructures import AttributeDict

from event_pubsub.consumers.marketplace_event_consumer.mpe_event_consumer import MPEEventConsumer
from event_pubsub.consumers.marketplace_event_consumer.organization_event_consumer import OrganizationEventConsumer
from event_pubsub.producers.blockchain_event_producer import BlockchainEventProducer


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass


    def test_on_event(self):
      # event= {"data":{'row_id': 347, 'block_no': 6629145, 'event': 'ChannelOpen',
      #                   'json_str': '{\'sender\': \'0x669CCF5025C08304Fd836d7A136634E22C5Dd31C\', \'recipient\': \'0xaceB1EaCA36061ff29Ddb7c963142abbFf23e508\', \'groupId\': b"\\xbc\\xb0\\xa1\\x93Z\\xa1\\xab\\x11\\xfd\\xbcX\\x1c\\x1cxZ\\xdc.\\xb6\\xba\\x8e\\xc6\\xc8C*\\xd7\\xa9\\xea\\x91\\xe6\'\\xae\\xfc", \'channelId\': 143, \'nonce\': 0, \'signer\': \'0x669CCF5025C08304Fd836d7A136634E22C5Dd31C\', \'amount\': 1, \'expiration\': 8731644}',
      #                   'processed': b'\x00',
      #                   'transactionHash': "b'\\xb7X\\xde\\x13{\\x13\\x05$\\x99\\x8c\\x1a\\xe4\\xae\\xdf\\x0f\\x88\\x08\\xd4\\x0f\\x7fVV^T;s\\x93\\x90$?\\xe6\\x14'",
      #                   'logIndex': '42', 'error_code': 1, 'error_msg': '',
      #                   'row_updated': datetime(2019, 10, 23, 12, 35, 53),
      #                   'row_created': datetime(2019, 10, 23, 12, 35, 53)},"name":"ChannelOpen"}

    #<

      event={"data":{'row_id': 349, 'block_no': 6629307, 'event': 'ChannelAddFunds',
                    'json_str': "{'channelId': 117, 'additionalFunds': 10}", 'processed': b'\x00',
                    'transactionHash': "b'\\x14\\xb3\\x8b\\x18\\xf1@6\\xe7\\x85T\\x82\\xf3\\xe7\\x15\\x82U\\xd8(\\x0f\\xe8T\\xac\\xdb\\xbdg\\xad0s\\xb6\\xd8\\x03\\x98'",
                    'logIndex': '4', 'error_code': 1, 'error_msg': '',
                    'row_updated': datetime(2019, 10, 23, 12, 35, 53),
                    'row_created': datetime(2019, 10, 23, 12, 35, 53)},"name":"ChannelAddFunds"}
    #
    # <
    #
    # class 'dict'>: {'row_id': 348, 'block_no': 6629094, 'event': 'ChannelSenderClaim',
    #                 'json_str': "{'channelId': 43, 'nonce': 1, 'claimAmount': 0}", 'processed': b'\x00',
    #                 'transactionHash': 'b\'\\x17\\xd6\\xf2[\\xcae\\x0f\\xa6\\x9e\\xbe"_\\x13"\\x15}\\xfaT\\x89\\x19\\xa1\\xf6\\xe8\\xc4\\xbf\\xa9gy\\x89W%\\x93\'',
    #                 'logIndex': '26', 'error_code': 1, 'error_msg': '',
    #                 'row_updated': datetime.datetime(2019, 10, 23, 12, 35, 53),
    #                 'row_created': datetime.datetime(2019, 10, 23, 12, 35, 53)}

      org_event_consumer=MPEEventConsumer("wss://ropsten.infura.io/ws","http://ipfs.singularitynet.io")
      org_event_consumer.on_event(event=event)

        #blockchain_vents = org_event_consumer.organization_dao.read_registry_events()
      print(123)



if __name__ == "__main__":
    unittest.main()
