import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from common.constant import TransactionStatus
from common.repository import Repository
from wallets.handlers.channel_handler import record_create_channel_event
from wallets.infrastructure.models import CreateChannelEvent, ChannelTransactionHistory
from wallets.infrastructure.repositories.channel_repository import ChannelRepository
from wallets.service.channel_service import channel_repo
from wallets.service.manage_create_channel_event import ManageCreateChannelEvent
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
        ManageCreateChannelEvent().manage_create_channel_event()
        channel_create_events = channel_dao.get_one_create_channel_event(TransactionStatus.PENDING)
        if channel_create_events is None:
            assert True

    def test_create_channel_even_consumer_no_data(self):
        ManageCreateChannelEvent().manage_create_channel_event()

    def test_record_create_channel_create(self):
        self.tearDown()
        event = {"body": json.dumps({
            "order_id": "sample_order_id",
            "sender": "sample_sender",
            "signature": "sample_signature",
            "r": "sample_r",
            "s": "sample_s",
            "v": 27,
            "group_id": "sample_group_id",
            "org_id": "sample_org_id",
            "amount": 2,
            "currency": "USD",
            "recipient": "sample_recipient",
            "current_block_no": 10764919,
            "amount_in_cogs": 100000
        })}
        res = record_create_channel_event(event=event, context=None)
        assert res["statusCode"] == 201
        record = ChannelRepository().get_channel_transaction_history_data(status=TransactionStatus.NOT_SUBMITTED)
        assert record[0].to_dict() == {'order_id': 'sample_order_id', 'amount': 2, 'currency': 'USD', 'type': '',
                                       'address': 'sample_sender', 'recipient': 'sample_recipient',
                                       'signature': 'sample_signature',
                                       'org_id': 'sample_org_id', 'group_id': 'sample_group_id',
                                       'request_parameters': '',
                                       'transaction_hash': '', 'status': 'NOT_SUBMITTED'}

    def tearDown(self):
        channel_repo.session.query(CreateChannelEvent).delete()
        channel_repo.session.query(ChannelTransactionHistory).delete()
        channel_repo.session.commit()
