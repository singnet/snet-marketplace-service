import json
import unittest
from event_pubsub.config import NETWORKS, NETWORK_ID
from event_pubsub.constants import EventType
from event_pubsub.event_repository import EventRepository
from event_pubsub.handlers.raw_events_handler import get_raw_event_details
from event_pubsub.infrastructure.models import MpeEventsRaw
from event_pubsub.infrastructure.repositories.mpe_event_repo import MPEEventRepository
from event_pubsub.repository import Repository

connection = Repository(NETWORKS=NETWORKS, NETWORK_ID=NETWORK_ID)
event_repository = EventRepository(connection)
channel_repo = MPEEventRepository()


class EventPubsubService(unittest.TestCase):
    def setUp(self):
        self.tearDown()
        MPEEventRepository().add_item(item=
        MpeEventsRaw(
            block_no=10259540,
            uncle_block_no=12,
            event="ChannelOpen",
            json_str='{''sender'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''amount'': 1000000000}',
            processed=1,
            transactionHash="0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3",
            logIndex="3",
            error_code="200",
            error_msg="",
            row_updated='2021-05-18 16:21:51',
            row_created='2021-05-18 16:21:51'
        ))
        MPEEventRepository().add_item(item=
        MpeEventsRaw(
            block_no=10259527,
            uncle_block_no=23,
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
        MPEEventRepository().add_item(item=
        MpeEventsRaw(
            block_no=10259523,
            uncle_block_no=21,
            event="DepositFunds",
            json_str='{''sender'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''amount'': 1000000000}',
            processed=0,
            transactionHash="sample_hash",
            logIndex="6",
            error_code="200",
            error_msg="",
            row_updated='2021-05-18 16:21:51',
            row_created='2021-05-18 16:21:51'
        ))

    def test_get_mpe_processed_transactions(self):
        event = {
            "transaction_hash_list": [
                "0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3",
                "0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3",
                "sample_hash"
            ],
            "event_name": EventType.MPE.value,
        }
        res = get_raw_event_details(event=event, context=None)
        assert res['statusCode'] == 200
        assert json.loads(res["body"])["data"] == [
            {
                "block_no": 10259540,
                "uncle_block_no": 12,
                "event": "ChannelOpen",
                "json_str": "{sender: 0xC67634c07EA0625b3Ad61d519a96fd44D7545F24, amount: 1000000000}",
                "processed": 1,
                "transactionHash": "0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3",
                "logIndex": "3",
                "error_code": 200,
                "error_msg": ""
            },
            {
                "block_no": 10259527,
                "uncle_block_no": 23,
                "event": "DepositFunds",
                "json_str": "{sender: 0xC67634c07EA0625b3Ad61d519a96fd44D7545F24, amount: 1000000000}",
                "processed": 1,
                "transactionHash": "0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3",
                "logIndex": "6",
                "error_code": 200,
                "error_msg": ""
            },
            {
                "block_no": 10259523,
                "uncle_block_no": 21,
                "event": "DepositFunds",
                "json_str": "{sender: 0xC67634c07EA0625b3Ad61d519a96fd44D7545F24, amount: 1000000000}",
                "processed": 0,
                "transactionHash": "sample_hash",
                "logIndex": "6",
                "error_code": 200,
                "error_msg": ""
            }]

    def tearDown(self):
        channel_repo.session.query(MpeEventsRaw).delete()
        channel_repo.session.commit()
