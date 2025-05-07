import json
import unittest
from unittest.mock import patch

from common.utils import validate_dict
from orchestrator.services.wallet_service import WalletService


class TestWalletClientService(unittest.TestCase):

    @patch("orchestrator.services.wallet_service.WalletService.get_channel_transactions")
    @patch("orchestrator.services.wallet_service.WalletService.get_channels_from_contract")
    def test_get_channel_details(self, mock_channels_from_contract, mock_channel_transactions):
        mock_channel_transactions.return_value = [
            {
                "address": "0x123",
                "is_default": 1,
                "type": "GENERAL",
                "transactions": [
                    {
                        "org_id": "snet",
                        "group_id": "default-group",
                        "recipient": "0x123",
                        "amount": 123,
                        "transaction_type": "channelAddFunds",
                        "currency": "USD",
                        "status": "PENDING",
                        "created_at": "2019-10-18 09:59:13"
                    }
                ]
            }
        ]
        mock_channels_from_contract.return_value = [
            {
                "channel_id": 117,
                "recipient": "0x234",
                "balance_in_cogs": "135.00000000",
                "pending": "0E-8",
                "nonce": 0,
                "expiration": 11111111,
                "signer": "0x345",
                "status": "active"
            }
        ]

        username = "dummy@dummy.io"
        org_id = "dummy"
        group_id = "dummy-group"

        channel_details = WalletService().get_channel_details(username, org_id, group_id)
        assert validate_dict(channel_details, ["username", "org_id", "group_id", "wallets"])
        assert isinstance(channel_details["wallets"], list)
        assert validate_dict(channel_details["wallets"][0], ["channels"])
        assert isinstance(channel_details["wallets"][0]["channels"], list)

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_get_channel_transactions(self, invoke_lambda_mock):
        invoke_lambda_mock.return_value = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "data": {
                        "username": "dummy@dummy.io",
                        "wallets": [
                            {
                                "address": "0x123",
                                "is_default": 1,
                                "type": "GENERAL",
                                "transactions": [
                                    {
                                        "org_id": "snet",
                                        "group_id": "default-group",
                                        "recipient": "0x123",
                                        "amount": 123,
                                        "transaction_type": "channelAddFunds",
                                        "currency": "USD",
                                        "status": "PENDING",
                                        "created_at": "2019-10-18 09:59:13"
                                    }
                                ]
                            }
                        ]
                    }
                }
            )
        }
        username = "dummy@dummy.io"
        org_id = "dummy"
        group_id = "dummy-group"
        channel_transactions = WalletService().get_channel_transactions(username, org_id, group_id)
        assert isinstance(channel_transactions, list)

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_get_channels_from_contract(self, invoke_lambda_mock):
        invoke_lambda_mock.return_value = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "data": {
                        "username": "dummy@dummy.io",
                        "group_id": "dummy-group",
                        "org_id": "dummy",
                        "channels": [
                            {
                                "channel_id": 117,
                                "recipient": "0x234",
                                "balance_in_cogs": "135.00000000",
                                "pending": "0E-8",
                                "nonce": 0,
                                "expiration": 11111111,
                                "signer": "0x345",
                                "status": "active"
                            }
                        ]
                    }
                }
            )
        }
        username = "dummy@dummy.io"
        org_id = "dummy"
        group_id = "dummy-group"
        transaction_keys = ["channel_id", "recipient", "balance_in_cogs", "pending",
                            "nonce", "expiration", "signer", "status"]
        channel_transactions = WalletService().get_channels_from_contract(username, org_id, group_id)
        assert isinstance(channel_transactions, list)
        if len(channel_transactions) > 0:
            transaction = channel_transactions[0]
            assert validate_dict(transaction, transaction_keys)

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_get_wallets(self, invoke_lambda_mock):
        invoke_lambda_mock.return_value = {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "data": {
                    "username": "dummy@dummy.io",
                    "wallets": [
                        {
                            "address": "0x123",
                            "is_default": 1,
                            "type": "GENERAL",
                            "status": 0,
                            "private_key": "dummy"
                        }
                    ]
                },
            })
        }
        username = "dummy@dummy.io"
        wallet_required_keys = ["address", "is_default", "type", "status"]
        wallets = WalletService().get_wallets(username)
        assert isinstance(wallets, dict)
        assert "username" in wallets
        assert "wallets" in wallets
        if len(wallets["wallets"]) > 0:
            wallet_details = wallets["wallets"][0]
            assert validate_dict(wallet_details, wallet_required_keys)

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_register_wallet(self, invoke_lambda_mock):
        invoke_lambda_mock.return_value = {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "data": []
            })
        }

        username = "dummy@dummy.io"
        wallet_details = {
            "address": "0x123",
            "type": "METAMASK"
        }
        register_wallet_response = WalletService().register_wallet(username, wallet_details)
        assert isinstance(register_wallet_response, list)

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_set_default_wallet(self, invoke_lambda_mock):
        invoke_lambda_mock.return_value = {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "data": "OK"
            })
        }
        username = "dummy@dummy.io"
        address = "0x123"
        register_wallet_response = WalletService().set_default_wallet(username, address)
        self.assertEqual(register_wallet_response, "OK")

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_get_default_wallet(self, invoke_lambda_mock):
        invoke_lambda_mock.return_value = {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "data": {
                    "username": "dummy@dummy.io",
                    "wallets": [
                        {
                            "address": "0x123",
                            "is_default": 1,
                            "type": "GENERAL",
                            "status": 0,
                            "private_key": "dummy"
                        }
                    ]
                }
            })
        }
        username = "dummy@dummy.io"
        default_wallet = WalletService().get_default_wallet(username)
        assert isinstance(default_wallet, dict)
        assert validate_dict(default_wallet, ["address", "is_default", "type", "status"])
