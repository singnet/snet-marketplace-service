import json
import unittest
from unittest.mock import patch

from common.repository import Repository
from wallets import lambda_handler
from wallets.config import NETWORKS, NETWORK_ID


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

    @patch("common.utils.Utils.report_slack")
    def test_register_wallets(self, mock_report_slack):
        pass

    @patch("common.utils.Utils.report_slack")
    def test_set_default_wallet(self, mock_report_slack):
        pass

    def tearDown(self):
        self.repo.execute("DELETE FROM wallet")
        self.repo.execute("DELETE FROM user_wallet")
