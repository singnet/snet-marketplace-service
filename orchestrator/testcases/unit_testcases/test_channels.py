import json
import unittest
from unittest.mock import patch

import orchestrator.services.wallet_service
from orchestrator.lambda_handler import request_handler


class Test(unittest.TestCase):

    @patch("orchestrator.services.wallet_service.WalletService.get_channel_transactions")
    def test_get_channels(self, mock_channel_transactions):
        event = {
            "path": "/orchestrator/wallet/channel",
            "httpMethod": "GET",
            "requestContext": {
                "authorizer": {"claims": {"email": "fojeloy633@aline9.com"}}
            },
            "queryStringParameters": {
                "org_id": "ropsten_test_2807",
                "group_id": "ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM="
            }
        }
        mock_channel_transactions.return_value = [
            {'address': '0x93c8BF18e501fCCb2E24E4f998386D0bD575000a', 'is_default': 0, 'type': 'GENERAL',
             'transactions': [
                 {'org_id': 'ropsten_test_2807', 'group_id': 'ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM=',
                  'recipient': '0xCc3cD60FF9936B7C9272a649b24f290ADa562469', 'amount': 2,
                  'transaction_type': 'openChannelByThirdParty', 'currency': 'USD', 'status': 'FAILED',
                  'created_at': '2021-08-03 04:53:55'},
                 {'org_id': 'ropsten_test_2807', 'group_id': 'ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM=',
                  'recipient': '0xCc3cD60FF9936B7C9272a649b24f290ADa562469', 'amount': 2,
                  'transaction_type': 'openChannelByThirdParty', 'currency': 'USD', 'status': 'NOT_SUBMITTED',
                  'created_at': '2021-08-03 04:53:55'},
                 {'org_id': 'ropsten_test_2807', 'group_id': 'ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM=',
                  'recipient': '0xCc3cD60FF9936B7C9272a649b24f290ADa562469', 'amount': 2,
                  'transaction_type': 'openChannelByThirdParty', 'currency': 'USD', 'status': 'PROCESSING',
                  'created_at': '2021-08-03 04:53:55'}
             ], 'channels': [
                {'channel_id': 661, 'recipient': '0xCc3cD60FF9936B7C9272a649b24f290ADa562469',
                 'balance_in_cogs': '100000.00000000', 'consumed_balance': '0', 'current_balance': '100000.00000000',
                 'pending': '0E-8', 'nonce': 0, 'expiration': 31787523,
                 'signer': '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F', 'status': 'active'}]}]
        response = request_handler(event=event, context=None)
        assert response["statusCode"] == 200
        assert json.loads(response["body"])["data"] == {
            "username": "fojeloy633@aline9.com",
            "org_id": "ropsten_test_2807",
            "group_id": "ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM=",
            "wallets": [
                {
                    "address": "0x93c8BF18e501fCCb2E24E4f998386D0bD575000a",
                    "is_default": 0,
                    "type": "GENERAL",
                    "transactions": [
                        {
                            "org_id": "ropsten_test_2807",
                            "group_id": "ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM=",
                            "recipient": "0xCc3cD60FF9936B7C9272a649b24f290ADa562469",
                            "amount": 2,
                            "transaction_type": "openChannelByThirdParty",
                            "currency": "USD",
                            "status": "FAILED",
                            "created_at": "2021-08-03 04:53:55"
                        },
                        {
                            "org_id": "ropsten_test_2807",
                            "group_id": "ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM=",
                            "recipient": "0xCc3cD60FF9936B7C9272a649b24f290ADa562469",
                            "amount": 2,
                            "transaction_type": "openChannelByThirdParty",
                            "currency": "USD",
                            "status": "PENDING",
                            "created_at": "2021-08-03 04:53:55"
                        },
                        {
                            "org_id": "ropsten_test_2807",
                            "group_id": "ukyXS9a2zJFDo2lFqn0IOEga6o6YOXYbl8ADW6ekTFM=",
                            "recipient": "0xCc3cD60FF9936B7C9272a649b24f290ADa562469",
                            "amount": 2,
                            "transaction_type": "openChannelByThirdParty",
                            "currency": "USD",
                            "status": "PENDING",
                            "created_at": "2021-08-03 04:53:55"
                        }
                    ],
                    "channels": [
                        {
                            "channel_id": 661,
                            "recipient": "0xCc3cD60FF9936B7C9272a649b24f290ADa562469",
                            "balance_in_cogs": "100000.00000000",
                            "consumed_balance": "0",
                            "current_balance": "100000.00000000",
                            "pending": "0E-8",
                            "nonce": 0,
                            "expiration": 31787523,
                            "signer": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
                            "status": "active"
                        }
                    ]
                }
            ]
        }
