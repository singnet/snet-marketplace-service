import json
import unittest
from types import SimpleNamespace as Namespace
from unittest.mock import patch

from common.constant import TransactionStatus
from wallets.handlers.channel_transaction_status_handler import request_handler
from wallets.handlers.wallet_handlers import add_or_update_channel_transaction_history
from wallets.infrastructure.models import ChannelTransactionHistory
from wallets.infrastructure.repositories.channel_repository import ChannelRepository

channel_repo = ChannelRepository()


class TestChannelService(unittest.TestCase):

    @patch(
        "wallets.service.channel_transaction_status_service.ChannelTransactionStatusService"
        ".get_mpe_processed_transactions_from_event_pub_sub")
    @patch("common.blockchain_util.BlockChainUtil.get_transaction_receipt_from_blockchain")
    def test_channel_update_transaction_status(self, mock_reciept, mock_processed_res):
        self.tearDown()
        channel_repo.add_item(ChannelTransactionHistory(
            order_id="sample_order_id",
            amount=2,
            currency="USD",
            type="openChannelByThirdParty",
            address="sample_address",
            recipient="sample_recipient",
            signature="sample_signature",
            org_id="sample_org_id",
            group_id="sample_group_id",
            request_parameters="sample",
            transaction_hash="sample_1",
            status="PENDING",
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))
        channel_repo.add_item(ChannelTransactionHistory(
            order_id="sample_order_id",
            amount=2,
            currency="USD",
            type="openChannelByThirdParty",
            address="sample_address",
            recipient="sample_recipient",
            signature="sample_signature",
            org_id="sample_org_id",
            group_id="sample_group_id",
            request_parameters="sample",
            transaction_hash="sample_2",
            status="PENDING",
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))
        channel_repo.add_item(ChannelTransactionHistory(
            order_id="sample_order_id",
            amount=2,
            currency="USD",
            type="openChannelByThirdParty",
            address="sample_address",
            recipient="sample_recipient",
            signature="sample_signature",
            org_id="sample_org_id",
            group_id="sample_group_id",
            request_parameters="sample_3",
            transaction_hash="sample_3",
            status="PENDING",
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))
        mock_processed_res.return_value = mock_processed_res.return_value = [
            {
                "block_no": 10259540,
                "uncle_block_no": 12,
                "event": "ChannelOpen",
                "json_str": "{sender: 0xC67634c07EA0625b3Ad61d519a96fd44D7545F24, amount: 1000000000}",
                "processed": 1,
                "transactionHash": "sample_1",
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
                "transactionHash": "sample_2",
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
                "transactionHash": "sample_3",
                "logIndex": "6",
                "error_code": 200,
                "error_msg": ""
            }
        ]
        mock_reciept.return_value = json.loads('{"status": 1}', object_hook=lambda d: Namespace(**d))
        res = request_handler(event={}, context=None)
        transaction = channel_repo.get_channel_transaction_history_data()
        assert transaction[0].transaction_hash == "sample_1"
        assert transaction[0].status == TransactionStatus.SUCCESS
        assert transaction[1].transaction_hash == "sample_2"
        assert transaction[1].status == TransactionStatus.SUCCESS
        assert transaction[2].transaction_hash == "sample_3"
        assert transaction[2].status == TransactionStatus.PROCESSING

        self.tearDown()
        channel_repo.add_item(ChannelTransactionHistory(
            order_id="sample_order_id",
            amount=2,
            currency="USD",
            type="openChannelByThirdParty",
            address="sample_address",
            recipient="sample_recipient",
            signature="sample_signature",
            org_id="sample_org_id",
            group_id="sample_group_id",
            request_parameters="sample",
            transaction_hash="sample_1",
            status="PENDING",
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))
        mock_reciept.return_value = json.loads('{"status": 0}', object_hook=lambda d: Namespace(**d))
        res = request_handler(event={}, context=None)
        transaction = channel_repo.get_channel_transaction_history_data()
        assert transaction[0].transaction_hash == "sample_1"
        assert transaction[0].status == TransactionStatus.FAILED

    def test_add_or_update_channel_transaction_history(self):
        self.tearDown()
        event = {
            "order_id": "bed8dd46-b89e-11eb-8e43-ca4f96114fea",
            "amount": 2,
            "currency": "USD",
            "type": "openChannelByThirdParty",
            "address": "",
            "recipient": "",
            "signature": "",
            "org_id": "test_rt_v2",
            "group_id": "JDdUEF1S+Ti/AdH7AhlIMGo1WbEp6T51b6tJGF0RTJg=",
            "request_parameters": "",
            "transaction_hash": "",
            "status": "",
            "row_created": "2020-08-04 00:00:03",
            "row_updated": "2020-08-04 00:00:03"
        }
        res = add_or_update_channel_transaction_history(event=event, context=None)
        assert res['statusCode'] == 200
        assert json.loads(res["body"])["data"] == {
            "order_id": "bed8dd46-b89e-11eb-8e43-ca4f96114fea",
            "amount": 2,
            "currency": "USD",
            "type": "openChannelByThirdParty",
            "address": "",
            "recipient": "",
            "signature": "",
            "org_id": "test_rt_v2",
            "group_id": "JDdUEF1S+Ti/AdH7AhlIMGo1WbEp6T51b6tJGF0RTJg=",
            "request_parameters": "",
            "transaction_hash": "",
            "status": ""
        }

        event = {
            "order_id": "bed8dd46-b89e-11eb-8e43-ca4f96114fea",
            "amount": 2,
            "currency": "USD",
            "type": "openChannelByThirdParty",
            "address": "",
            "recipient": "",
            "signature": "",
            "org_id": "test_rt_v2",
            "group_id": "JDdUEF1S+Ti/AdH7AhlIMGo1WbEp6T51b6tJGF0RTJg=",
            "request_parameters": "",
            "transaction_hash": "sample_update_test_hash",
            "status": "update_status_check",
            "row_created": "2020-08-04 00:00:03",
            "row_updated": "2020-08-04 00:00:03"
        }
        res = add_or_update_channel_transaction_history(event=event, context=None)
        assert res['statusCode'] == 200
        assert json.loads(res["body"])["data"] == {
            "order_id": "bed8dd46-b89e-11eb-8e43-ca4f96114fea",
            "amount": 2,
            "currency": "USD",
            "type": "openChannelByThirdParty",
            "address": "",
            "recipient": "",
            "signature": "",
            "org_id": "test_rt_v2",
            "group_id": "JDdUEF1S+Ti/AdH7AhlIMGo1WbEp6T51b6tJGF0RTJg=",
            "request_parameters": "",
            "transaction_hash": "sample_update_test_hash",
            "status": "update_status_check"
        }
        data = ChannelRepository().get_channel_transaction_history_data(transaction_hash="sample_update_test_hash")
        assert data[0].status == "update_status_check"

    def tearDown(self):
        channel_repo.session.query(ChannelTransactionHistory).delete()
        channel_repo.session.commit()
