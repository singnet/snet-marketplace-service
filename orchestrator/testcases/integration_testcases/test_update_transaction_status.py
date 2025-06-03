import unittest
import json
from unittest.mock import patch

from common.repository import Repository
from orchestrator.config import NETWORK_ID, NETWORKS
from orchestrator.handlers.cancel_order_handler import request_handler as cancel_given_order
from orchestrator.handlers.update_transaction_status_handler import request_handler


class TestUpdateTransaction(unittest.TestCase):
    def setUp(self):
        repo = Repository(net_id = NETWORK_ID, NETWORKS = NETWORKS)
        repo.execute("INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated) VALUES('dummy1@dummy.io', 'cb736cfa-dae4-11e9-9769-26327914c219', 'TOP_UP', '{}', 'PAYMENT_INITIATION_FAILED', NOW()- INTERVAL - -20 MINUTE, NOW());")
        repo.execute("INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated) VALUES('dummy2@dummy.io', 'db736cfa-dae4-11e9-9769-26327914c219', 'CREATE_CHANNEL', '{}', 'PAYMENT_INITIATION_FAILED', NOW()- INTERVAL - -20 MINUTE, NOW());")
        repo.execute("INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated) VALUES('dummy3@dummy.io', 'eb736cfa-dae4-11e9-9769-26327914c219', 'CREATE_WALLET_AND_CHANNEL', '{}', 'PAYMENT_INITIATION_FAILED', NOW()- INTERVAL - -20 MINUTE, NOW());")
        repo.execute("INSERT INTO transaction_history (username, order_id, order_type, raw_payment_data, status, row_created, row_updated) VALUES('dummy4@dummy.io', 'Fb736cfa-dae4-11e9-9769-26327914c219', 'CREATE_WALLET_AND_CHANNEL', '{}', 'PAYMENT_INITIATION_FAILED', NOW()- INTERVAL - -20 MINUTE, NOW());")

    @patch("common.utils.Utils.report_slack")
    def test_update_transaction_status(self, mock_report_slack):
        response = request_handler(event={}, context=None)
        assert (response == "success")
        repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        query_response = repo.execute("SELECT * FROM transaction_history WHERE status = %s", ["ORDER_CANCELED"])
        assert (len(query_response) > 1)

    @patch("common.utils.Utils.report_slack")
    def test_cancel_given_order(self, mock_report_slack):
        event = {"path": "/orchestrator/order/Fb736cfa-dae4-11e9-9769-26327914c219/cancel",
                 "pathParameters": {"order_id": "Fb736cfa-dae4-11e9-9769-26327914c219"}, "httpMethod": "GET"}
        response = cancel_given_order(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        query_response = repo.execute("SELECT * FROM transaction_history WHERE order_id = %s AND status = %s", ["Fb736cfa-dae4-11e9-9769-26327914c219", "ORDER_CANCELED"])
        assert (len(query_response) == 1)

    def tearDown(self):
        repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        repo.execute("DELETE FROM transaction_history WHERE username in ('dummy1@dummy.io', 'dummy2@dummy.io', 'dummy3@dummy.io', 'dummy4@dummy.io')")
