import unittest
from unittest.mock import patch

from wallets.application.service.wallet_service import WalletService
from wallets.domain.models.wallet import WalletModel
from wallets.infrastructure.models import Wallet, UserWallet
from wallets.infrastructure.repositories.wallet_repository import WalletRepository


class TestWalletService(unittest.TestCase):
    def setUp(self):
        self.wallet_service = WalletService()
        self.wallet_repo = WalletRepository()

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
        username = "dummy@dummy.io"
        wallet = WalletModel(address="32344958712265144",
                        type="GENERAL",
                        status=0)
        self.wallet_repo.insert_wallet(wallet)
        self.wallet_repo.add_user_for_wallet(wallet, username)
        self.wallet_service.remove_user_wallet(username)
        wallet_details = self.wallet_repo.get_wallet_data_by_username(username)
        if len(wallet_details) == 0:
            assert True
        else:
            assert False

    def tearDown(self):
        self.wallet_repo.session.begin()
        self.wallet_repo.session.query(Wallet).delete()
        self.wallet_repo.session.query(UserWallet).delete()
        self.wallet_repo.session.commit()
