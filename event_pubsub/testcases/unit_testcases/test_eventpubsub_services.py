import json
import unittest
from datetime import datetime as dt
from event_pubsub.config import NETWORKS, NETWORK_ID
from event_pubsub.event_repository import EventRepository
from event_pubsub.handlers.lambda_handler import get_mpe_processed_transactions
from event_pubsub.infrastructure.models import MpeEventsRaw
from event_pubsub.infrastructure.repositories.channel_repo import ChannelRepo
from event_pubsub.repository import Repository

connection = Repository(NETWORKS=NETWORKS, NETWORK_ID=NETWORK_ID)
event_repository = EventRepository(connection)
channel_repo = ChannelRepo()


class EventPubsubService(unittest.TestCase):
    def setUp(self):
        self.tearDown()
        ChannelRepo().add_item(item=
        MpeEventsRaw(
            block_no=10259540,
            event="ChannelOpen",
            json_str='{''sender'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''recipient'': ''0xabd2cCb3828b4428bBde6C2031A865b0fb272a5A'', ''groupId'': b''\\xbe\\\\Pj\\x12\\xe0\\x8eS\\xba\\xa2\\x89\\x9b\\x82 \\xcca\\x16R\\xfbb:\\xce\\xd4\\xd2aU_ \\xf5LfI'', ''channelId'': 0, ''nonce'': 0, ''signer'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''amount'': 1, ''expiration'': 12402257}',
            processed=1,
            transactionHash="0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3",
            logIndex="3",
            error_code="200",
            error_msg="",
            row_updated='2021-05-18 16:21:51',
            row_created='2021-05-18 16:21:51'
        ))
        ChannelRepo().add_item(item=
        MpeEventsRaw(
            block_no=10259527,
            event="DepositFunds",
            json_str='{''sender'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''amount'': 1000000000}',
            processed=1,
            transactionHash="0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3",
            logIndex="6",
            error_code="200",
            error_msg="",
            row_updated='2021-05-18 16:21:51',
            row_created='2021-05-18 16:21:51'
        ))

    def test_get_mpe_processed_transactions(self):
        event = {"transaction_list": ["0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3",
                                      "0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3"]}
        res = get_mpe_processed_transactions(event=event, context=None)
        assert res['statusCode'] == 200
        assert json.loads(res["body"])["data"] == ["0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3",
                                                   "0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3"]

    def tearDown(self):
        channel_repo.session.query(MpeEventsRaw).delete()
        channel_repo.session.commit()