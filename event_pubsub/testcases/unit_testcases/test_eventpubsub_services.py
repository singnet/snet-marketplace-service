import json
import unittest

from event_pubsub.config import NETWORKS
from event_pubsub.event_repository import EventRepository
from event_pubsub.handlers.lambda_handler import get_mpe_processed_transactions
from event_pubsub.repository import Repository

connection = Repository(NETWORKS=NETWORKS)
event_repository = EventRepository(connection)

class EventPubsubService(unittest.TestCase):
    pass

    def test_get_mpe_processed_transactions(self):
        self.tearDown()
        connection.begin_transaction()
        connection.execute("""
                        INSERT INTO mpe_events_raw (block_no,uncle_block_no,event,json_str,processed,transactionHash,logIndex,error_code,error_msg,row_updated,row_created) VALUES
                        (10259540,10259540,'ChannelOpen','{''sender'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''recipient'': ''0xabd2cCb3828b4428bBde6C2031A865b0fb272a5A'', ''groupId'': b''\\xbe\\\\Pj\\x12\\xe0\\x8eS\\xba\\xa2\\x89\\x9b\\x82 \\xcca\\x16R\\xfbb:\\xce\\xd4\\xd2aU_ \\xf5LfI'', ''channelId'': 0, ''nonce'': 0, ''signer'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''amount'': 1, ''expiration'': 12402257}',1,'0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3','3',200,'','2021-05-18 16:21:51','2021-05-18 16:21:51'),
                        (10259527,10259527,'DepositFunds','{''sender'': ''0xC67634c07EA0625b3Ad61d519a96fd44D7545F24'', ''amount'': 1000000000}',1,'0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3','6',200,'','2021-05-18 16:21:51','2021-05-18 16:21:51'),
                        (10265536,10265536,'DepositFunds','{''sender'': ''0xabd2cCb3828b4428bBde6C2031A865b0fb272a5A'', ''amount'': 50000000}',0,'0x41bb75d6c542b9807ce776604520a4ca0f1178acbfe7c5e6d433852d0fbd666e','12',200,'','2021-05-19 12:25:51','2021-05-19 12:25:51');""")
        connection.commit_transaction()

        event = {"transaction_list": ["0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3", "0x41bb75d6c542b9807ce776604520a4ca0f1178acbfe7c5e6d433852d0fbd666e","0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3"]}
        res = get_mpe_processed_transactions(event=event, context=None)
        assert res['statusCode'] == 200
        assert json.loads(res["body"])["data"] == ["0x027262535e8ba5e26e8a0938b29dd07e5887ed0eec832bac725a12e0127a07f3", "0x714e00dd9b023f497cba1a03628e9cbb8b007f1e02fa97fb3291ee7251198cc3"]

    def tearDown(self):
        connection.begin_transaction()
        connection.execute("delete from mpe_events_raw")
        connection.commit_transaction()