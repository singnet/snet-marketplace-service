import json
import unittest
from unittest.mock import patch

from common.repository import Repository
from wallets import lambda_handler
from wallets.config import NETWORKS, NETWORK_ID
from wallets.infrastructure.models import ChannelTransactionHistory, Wallet, UserWallet
from wallets.infrastructure.repositories.channel_repository import ChannelRepository

channel_repo = ChannelRepository()


class TestWalletAPI(unittest.TestCase):
    def setUp(self):
        self.NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    @patch("common.utils.Utils.report_slack")
    @patch("common.blockchain_util.BlockChainUtil.create_account")
    def test_create_wallet(self, mock_create_account, mock_report_slack):
        create_wallet_event = {
            "path": "/wallet",
            "httpMethod": "POST",
            "body": '{"username": "dummy@dummy.com"}',
        }
        mock_create_account.return_value = (
            "323449587122651441342932061624154600879572532581",
            "26561428888193216265620544717131876925191237116680314981303971688115990928499",
        )
        response = lambda_handler.request_handler(create_wallet_event,
                                                  context=None)
        assert response["statusCode"] == 200
        response_body = json.loads(response["body"])
        assert response_body["status"] == "success"
        assert (response_body["data"]["address"] ==
                "323449587122651441342932061624154600879572532581")
        assert (
            response_body["data"]["private_key"] ==
            "26561428888193216265620544717131876925191237116680314981303971688115990928499"
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
        pass

    def test_get_wallet_details(self):
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
            "path": "/wallet/channel/transactions",
            "httpMethod": "GET",
            "queryStringParameters": {
                "username": "sample_user",
                "org_id": "sample_org_id",
                "group_id": "sample_group_id"
            }

        }
        response = lambda_handler.request_handler(get_wallet_details,
                                                  context=None)
        assert response['statusCode'] == 200
        assert json.loads(response['body'])["data"] == {
            'username': 'sample_user',
            'wallets': [
                {'address': 'sample_address',
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
                 ]}]}

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
        response = lambda_handler.request_handler(get_wallet_details,
                                                  context=None)
        assert response['statusCode'] == 200
        assert json.loads(response['body'])["data"] == {
            'username': 'sample_user',
            'wallets': [
                {'address': 'sample_address',
                 'is_default': 0,
                 'type': 'GENERAL',
                 'transactions': []
                 }]}

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
