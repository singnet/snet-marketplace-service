import json
import unittest
from unittest.mock import patch

with patch("common.boto_utils.BotoUtils.get_ssm_parameter", return_value="744f676a485a4b63427a56342d476b6a3174324335536f375f65566f545735644553574a483663333554773d"):
    from wallets.application.handlers import wallet_handlers, channel_handlers
from wallets.infrastructure.models import ChannelTransactionHistory, Wallet, UserWallet
from wallets.infrastructure.repositories.channel_repository import ChannelRepository

channel_repo = ChannelRepository()


class TestWalletAPI(unittest.TestCase):
    @patch("common.utils.Utils.report_slack")
    @patch("common.blockchain_util.BlockChainUtil.create_account")
    def test_create_wallet(self, mock_create_account, mock_report_slack):
        create_wallet_event = {
            "body": '{"username": "dummy@dummy.com"}',
        }
        mock_create_account.return_value = (
            "323449587122651441342932061624154600879572532581",
            "2656142888819321626562054471713187692519123711668031498130397168",
        )
        response = wallet_handlers.create_and_register_wallet(create_wallet_event,
                                                  context=None)
        assert response["statusCode"] == 200
        response_body = json.loads(response["body"])
        assert response_body["status"] == "success"
        assert (response_body["data"]["address"] ==
                "323449587122651441342932061624154600879572532581")
        assert (
            response_body["data"]["private_key"] ==
            "2656142888819321626562054471713187692519123711668031498130397168"
        )
        assert response_body["data"]["status"] == 0
        assert response_body["data"]["type"] == "GENERAL"

    @patch("common.utils.Utils.report_slack")
    def test_create_wallet_and_channel(self, mock_report_slack):
        pass

    @patch("common.utils.Utils.report_slack")
    def test_create_channel(self, mock_report_slack):
        pass

    @patch("common.utils.Utils.report_slack")
    def test_top_up_channel(self, mock_report_slack):
        pass

    @patch("common.utils.Utils.report_slack")
    def test_get_wallet_details(self, mock_report_slack):
        self.tearDown()
        channel_repo.add_item(ChannelTransactionHistory(
            order_id="8c6b2568-f358-11eb-bd57-46eba0f9718d",
            amount=2,
            currency="USD",
            type="openChannelByThirdParty",
            address="sample_address",
            recipient="sample_recipient",
            signature="sample_signature",
            org_id="sample_org_id",
            group_id="sample_group_id",
            request_parameters="sample",
            transaction_hash="sample_hash",
            status="PENDING",
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))
        channel_repo.add_item(Wallet(
            address="sample_address",
            type="GENERAL",
            status=0,
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))
        channel_repo.add_item(UserWallet(
            username="sample_user",
            address="sample_address",
            is_default=0,
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))

        get_wallet_details = {
            "body": json.dumps({
                "username": "sample_user",
                "org_id": "sample_org_id",
                "group_id": "sample_group_id"
            })
        }
        response = channel_handlers.get_transactions_for_order(get_wallet_details,
                                                  context=None)
        assert response['statusCode'] == 200
        expected_dict = {
            'username': 'sample_user',
            'wallets': [
                {
                    'address': 'sample_address',
                    'is_default': 0,
                    'type': 'GENERAL',
                    'transactions': [
                        {
                            'org_id': 'sample_org_id',
                            'group_id': 'sample_group_id',
                            'recipient': 'sample_recipient',
                            'amount': 2,
                            'transaction_type': 'openChannelByThirdParty',
                            'currency': 'USD',
                            'status': 'PENDING',
                            'created_at': '2021-05-19 13:51:53'
                        }
                    ]
                }
            ]
        }
        real_dict = json.loads(response['body'])["data"]
        assert real_dict == expected_dict

        channel_repo.session.query(ChannelTransactionHistory).delete()
        channel_repo.session.commit()
        channel_repo.add_item(ChannelTransactionHistory(
            order_id="8c6b2568-f358-11eb-bd57-46eba0f9718d",
            amount=2,
            currency="USD",
            type="openChannelByThirdParty",
            address="sample_address",
            recipient="sample_recipient",
            signature="sample_signature",
            org_id="sample_org_id",
            group_id="sample_group_id",
            request_parameters="sample",
            transaction_hash="sample_hash",
            status="SUCCESS",
            row_updated="2021-05-19 13:51:53",
            row_created="2021-05-19 13:51:53"
        ))
        response = channel_handlers.get_transactions_for_order(get_wallet_details,
                                                  context=None)
        assert response['statusCode'] == 200
        expected_dict = {
            'username': 'sample_user',
            'wallets': [
                {'address': 'sample_address',
                 'is_default': 0,
                 'type': 'GENERAL',
                 'transactions': []
                 }]}
        real_dict = json.loads(response['body'])["data"]
        assert real_dict == expected_dict

    @patch("common.utils.Utils.report_slack")
    def test_register_wallets(self, mock_report_slack):
        pass

    @patch("common.utils.Utils.report_slack")
    def test_set_default_wallet(self, mock_report_slack):
        pass

    def tearDown(self):
        channel_repo.session.query(Wallet).delete()
        channel_repo.session.query(UserWallet).delete()
        channel_repo.session.query(ChannelTransactionHistory).delete()
        channel_repo.session.commit()
