import unittest
from unittest.mock import patch

from common.repository import Repository
from wallets.config import NETWORK_ID, NETWORKS
from wallets.dao.wallet_data_access_object import WalletDAO
from wallets.application.service import WalletService
from wallets.wallet import Wallet


class TestWalletService(unittest.TestCase):
    def setUp(self):
        self.NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        self.wallet_service = WalletService(repo=self.repo)

    @patch("common.utils.Utils.report_slack")
    @patch("common.blockchain_util.BlockChainUtil.create_account")
    def test_create_wallet(self, mock_create_account, mock_report_slack):
        mock_create_account.return_value = (
            "323449587122651441342932061624154600879572532581",
            "26561428888193216265620544717131876925191237116680314981303971688115990928499",
        )
        response = self.wallet_service.create_and_register_wallet(username="dummy")
        self.assertDictEqual(
            response,
            {"address": "323449587122651441342932061624154600879572532581",
             "private_key": "26561428888193216265620544717131876925191237116680314981303971688115990928499",
             "status": 0, "type": "GENERAL"
             }
        )

    @patch("common.utils.Utils.report_slack")
    @patch("wallets.dao.wallet_data_access_object.WalletDAO.get_wallet_details")
    @patch("wallets.dao.wallet_data_access_object.WalletDAO.insert_wallet")
    @patch("wallets.dao.wallet_data_access_object.WalletDAO.add_user_for_wallet")
    def test_register_wallet(self, mock_add_user_for_wallet, mock_insert_wallet,
                             mock_get_wallet_details, mock_report_slack):
        """
            insert new wallet for user
        """
        mock_get_wallet_details.return_value = []
        address = "323449587122651441342932061624154600879572532581"
        type = "GENERAL"
        status = 0
        username = "dummy@dummy.io"
        response = self.wallet_service.register_wallet(username, address, type, status)
        assert response
        self.assertRaises(Exception, self.wallet_service.register_wallet(username, address, type, status))

    def test_remove_user_wallet(self):
        wallet_dao = WalletDAO(self.repo)
        username = "dummy@dummy.io"
        wallet = Wallet(address="32344958712265144",
                        type="GENERAL",
                        status=0)
        wallet_dao.insert_wallet(wallet)
        wallet_dao.add_user_for_wallet(wallet, username)
        self.wallet_service.remove_user_wallet(username)
        wallet_details = wallet_dao.get_wallet_data_by_username(username)
        if len(wallet_details) == 0:
            assert True
        else:
            assert False

    def tearDown(self):
        self.repo.execute("DELETE FROM wallet")
        self.repo.execute("DELETE FROM user_wallet")
