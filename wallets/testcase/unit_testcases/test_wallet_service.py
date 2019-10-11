import json
import unittest
from unittest.mock import patch

from wallets import lambda_handler


class TestWalletService(unittest.TestCase):
    def setUp(self):
        pass

    @patch("common.utils.Utils.report_slack")
    @patch("common.blockchain_util.BlockChainUtil.create_account")
    def test_create_wallet(self, mock_create_account, mock_report_slack):
        pass
