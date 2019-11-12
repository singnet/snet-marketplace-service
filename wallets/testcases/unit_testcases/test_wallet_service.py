import unittest
from unittest.mock import patch

from common.repository import Repository
from wallets.config import NETWORK_ID, NETWORKS
from wallets.service.wallet_service import WalletService
from wallets.wallet import Wallet


class TestWalletService(unittest.TestCase):
    def setUp(self):
        self.NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
        self.db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS)) for netId in NETWORKS.keys())
        self.obj_wallet_manager = WalletService(obj_repo=self.db[NETWORK_ID])

    @patch("common.utils.Utils.report_slack")
    @patch("common.blockchain_util.BlockChainUtil.create_account")
    @patch("wallets.service.wallet_service.WalletService.register_wallet")
    def test_create_wallet(self, mock_register_wallet, mock_create_account, mock_report_slack):
        mock_register_wallet.return_value = True
        mock_create_account.return_value = (
            "323449587122651441342932061624154600879572532581",
            "26561428888193216265620544717131876925191237116680314981303971688115990928499",
        )
        response = self.obj_wallet_manager.create_and_register_wallet(username="dummy")
        assert (response == {"address": "323449587122651441342932061624154600879572532581",
                             "private_key": "26561428888193216265620544717131876925191237116680314981303971688115990928499",
                             "status": 0, "type": "GENERAL"})
        mock_register_wallet.return_value = False
        try:
            self.obj_wallet_manager.create_and_register_wallet(username="dummy")
        except Exception as e:
            assert (e.args == ("Unable to create and register wallet.",))

    @patch("common.utils.Utils.report_slack")
    @patch("wallets.dao.wallet_data_access_object.WalletDAO.insert_wallet_details")
    def test_register_wallet(self, mock_insert_wallet_details, mock_report_slack):
        mock_insert_wallet_details.return_value = True
        obj_wallet = Wallet(address="323449587122651441342932061624154600879572532581",
                            private_key="26561428888193216265620544717131876925191237116680314981303971688115990928499",
                            type="GENERAL", status=0)
        response = self.obj_wallet_manager.register_wallet(username="dummy", obj_wallet=obj_wallet)
        assert (response == True)
        mock_insert_wallet_details.return_value = False
        try:
            self.obj_wallet_manager.register_wallet(username="dummy", obj_wallet=obj_wallet)
        except Exception as e:
            assert (e.args == ("Unable to register wallet.",))


if __name__ == "__main__":
    unittest.main()
