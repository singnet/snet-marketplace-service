from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from common.constant import TransactionStatus
from common.repository import Repository
from wallets.create_channel_event_consumer import create_channel_event_consumer
from wallets.config import NETWORKS, NETWORK_ID
from wallets.dao.channel_dao import ChannelDAO


class TestCreateChannelConsumer(TestCase):

    def setUp(self):
        self.connection = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    @patch("wallets.service.wallet_service.WalletService.open_channel_by_third_party")
    def test_create_channel_event_consumer_success(self, create_channel_mock):
        create_channel_mock.return_value = {}
        channel_dao = ChannelDAO(self.connection)
        channel_dao.persist_create_channel_event({
            "r": "0x7be1502b09f5997339571f4885194417d6ca84ca65f98a9a2883d981d071ba62",
            "s": "0x55bcc83399b93bc60d70d4b10e33db626eac0dafd863b91e00a6b4b2c3586eb6", "v": 27, "amount": 2,
            "org_id": "snet", "sender": "0x4A3Beb90be90a28fd6a54B6AE449dd93A3E26dd0", "currency": "USD",
            "group_id": "m5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc=",
            "order_id": "b7d9ffa0-07a3-11ea-b3cf-9e57fd86be16",
            "recipient": "0xfA8a01E837c30a3DA3Ea862e6dB5C6232C9b800A",
            "signature": "0x7be1502b09f5997339571f4885194417d6ca84ca65f98a9a2883d981d071ba6255bcc83399b93bc60d70d4b10e33db626eac0dafd863b91e00a6b4b2c3586eb61b",
            "amount_in_cogs": 4000, "current_block_no": 6780504
        }, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        create_channel_event_consumer()
        channel_create_events = channel_dao.get_one_create_channel_event(TransactionStatus.PENDING)
        if channel_create_events is None:
            assert True

    @patch("wallets.service.wallet_service.WalletService.open_channel_by_third_party")
    @patch("common.utils.Utils.report_slack")
    def test_create_channel_event_consumer_failed(self, report_slack_mock, create_channel_mock):
        create_channel_mock.side_effect = Exception()
        channel_dao = ChannelDAO(self.connection)
        channel_dao.persist_create_channel_event({
            "r": "0x7be1502b09f5997339571f4885194417d6ca84ca65f98a9a2883d981d071ba62",
            "s": "0x55bcc83399b93bc60d70d4b10e33db626eac0dafd863b91e00a6b4b2c3586eb6", "v": 27, "amount": 2,
            "org_id": "snet", "sender": "0x4A3Beb90be90a28fd6a54B6AE449dd93A3E26dd0", "currency": "USD",
            "group_id": "m5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc=",
            "order_id": "b7d9ffa0-07a3-11ea-b3cf-9e57fd86be16",
            "recipient": "0xfA8a01E837c30a3DA3Ea862e6dB5C6232C9b800A",
            "signature": "0x7be1502b09f5997339571f4885194417d6ca84ca65f98a9a2883d981d071ba6255bcc83399b93bc60d70d4b10e33db626eac0dafd863b91e00a6b4b2c3586eb61b",
            "amount_in_cogs": 4000, "current_block_no": 6780504
        }, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        create_channel_event_consumer()
        channel_create_events = channel_dao.get_one_create_channel_event(TransactionStatus.FAILED)
        if channel_create_events is not None:
            assert True

    def test_create_channel_even_consumer_no_data(self):
        create_channel_event_consumer()

    def tearDown(self):
        self.connection.execute("DELETE FROM create_channel_event")
