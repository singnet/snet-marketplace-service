import unittest
from unittest.mock import patch

from wallets.application.service.wallet_service import WalletService
from wallets.domain.models.wallet import WalletModel
from wallets.infrastructure.models import Wallet, UserWallet
from wallets.infrastructure.repositories.wallet_repository import WalletRepository


class TestWalletService(unittest.TestCase):
    def setUp(self):
        with patch("common.boto_utils.BotoUtils.get_ssm_parameter",
                   return_value = "744f676a485a4b63427a56342d476b6a3174324335536f375f65566f545735644553574a483663333554773d"):
            self.wallet_service = WalletService()
        self.wallet_repo = WalletRepository()

    @patch("common.utils.Utils.report_slack")
    @patch("wallets.infrastructure.blockchain_util.BlockChainUtil.create_account")
    def test_create_wallet(self, mock_create_account, mock_report_slack):
        mock_create_account.return_value = (
            "323449587122651441342932061624154600879572532581",
            "2656142888819321626562054471713187692519123711668031498130397168",
        )
        response = self.wallet_service.create_and_register_wallet(username="dummy")
        self.assertDictEqual(
            response,
            {"address": "323449587122651441342932061624154600879572532581",
             "private_key": "2656142888819321626562054471713187692519123711668031498130397168",
             "status": 0, "type": "GENERAL"
             }
        )

    @patch("common.utils.Utils.report_slack")
    @patch("wallets.infrastructure.repositories.wallet_repository.WalletRepository.get_wallet_details")
    def test_register_wallet(self, mock_get_wallet_details, mock_report_slack):
        """
            insert new wallet for user
        """
        mock_get_wallet_details.return_value = []
        address = "323449587122651441342932061624154600879572532581"
        type = "GENERAL"
        status = 0
        username = "dummy@dummy.io"
        response = self.wallet_service.register_wallet(
            username = username,
            wallet_address = address,
            wallet_type = type,
            status = status
        )
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
        assert len(wallet_details) == 0

    def tearDown(self):
        self.wallet_repo.session.query(Wallet).delete()
        self.wallet_repo.session.query(UserWallet).delete()
        self.wallet_repo.session.commit()
