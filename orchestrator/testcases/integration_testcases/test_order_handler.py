import unittest
import json

from orchestrator.handlers.order_handler import currency_to_token_conversion
from unittest.mock import patch

class TestOrderHandler(unittest.TestCase):
    def setUp(self):
        pass

    @patch("common.utils.Utils.report_slack")
    def test_currency_to_token_conversion(self, mock_report_slack):
        event = {"pathParameters": {"currency": "USD"}, "queryStringParameters": {"amount": "100"}}
        response = currency_to_token_conversion(event=event, context=None)
        print(response)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["amount_in_cogs"] == "100")
        assert (response_body["data"]["amount_in_agi"] == "0.00000100")

