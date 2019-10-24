import json
import unittest
from unittest.mock import patch

from common.repository import Repository
from common.utils import validate_dict
from orchestrator.config import NETWORK_ID, NETWORKS
from orchestrator.services.order_service import OrderService


class TestOrderService(unittest.TestCase):

    def setUp(self):
        self.NETWORKS_NAME = dict((NETWORKS[netId]["name"], netId) for netId in NETWORKS.keys())
        self.db = dict((netId, Repository(net_id=netId, NETWORKS=NETWORKS)) for netId in NETWORKS.keys())
        self.order_service = OrderService(self.db[NETWORK_ID])

    def test_initiate_order(self):
        pass

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_manage_create_order(self, mock_lambda_invoke):
        mock_lambda_invoke.return_value = {
            'statusCode': 201,
            'body': json.dumps(
                {
                    "order_id": "e33404a2-f574-11e9-9a93-3abe2d8567d5",
                    "item_details": {
                        "item": "AGI",
                        "quantity": 1,
                        "org_id": "snet",
                        "group_id": "GROUP-123",
                        "service_id": "freecall",
                        "recipient": "0x123",
                        "order_type": "CREATE_WALLET_AND_CHANNEL",
                        "wallet_address": "",
                        "channel_id": ""
                    },
                    "price": {
                        "amount": 1,
                        "currency": "USD"
                    }
                }
            )
        }
        username = "dummy@dummy.io"
        item_details = {
            "item": "AGI",
            "quantity": 1,
            "org_id": "snet",
            "group_id": "GROUP-123",
            "service_id": "freecall",
            "recipient": "0x123",
            "order_type": "CREATE_WALLET_AND_CHANNEL",
            "wallet_address": "",
            "channel_id": ""
        }
        price = {
            "amount": 1, "currency": "USD"
        }
        order_details = self.order_service.manage_create_order(username, item_details, price)
        assert validate_dict(order_details, ["order_id", "item_details", "price"])

    def test_manage_initiate_payment(self):
        pass

    def test_execute_order(self):
        pass

    def test_manage_execute_payment(self):
        pass

    def test_manage_process_order(self):
        pass

    def test_get_payment_address_for_org(self):
        pass

    def test_get_channel_for_topup(self):
        pass

    def test_get_order_details_by_order_id(self):
        pass

    def test_get_order_details_by_username(self):
        pass
