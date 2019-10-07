import json
import unittest
from unittest.mock import patch

from signer import lambda_handler


class TestSignUPAPI(unittest.TestCase):
    def setUp(self):
        self.signature_for_free_call = {
            "path": "/free-call",
            "httpMethod": "GET",
            "queryStringParameters": {
                "org_id": "test-org",
                "service_id": "test-service-id",
            },
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy@dummy.com"
                    }
                }
            },
        }
        self.signature_for_regular_call = {
            "path": "/signer/regular-call",
            "httpMethod": "POST",
            "body": '{"channel_id": 1, "nonce": 6487832, "amount": 1}',
            "requestContext": {
                "stage": "ropsten",
                "authorizer": {
                    "claims": {
                        "email": "dummy@dummy.com"
                    }
                },
            },
        }

        self.signature_for_state_service = {
            "path": "/state-service",
            "httpMethod": "POST",
            "body": '{"channel_id": 1}',
            "requestContext": {
                "stage": "ropsten",
                "authorizer": {
                    "claims": {
                        "email": "dummy@dummy.com"
                    }
                },
            },
        }

    @patch("common.utils.Utils.report_slack")
    def test_signature_for_free_call(self, report_slack_mock):
        pass

    @patch("common.utils.Utils.report_slack")
    @patch("common.blockchain_util.BlockChainUtil.get_current_block_no")
    def test_signature_for_state_service(self, mock_current_block_no,
                                         mock_report_slack):
        mock_current_block_no.return_value = 6521925
        response = lambda_handler.request_handler(
            event=self.signature_for_state_service, context=None)
        assert response["statusCode"] == 200
        response_body = json.loads(response["body"])
        assert response_body["status"] == "success"
        assert (
            response_body["data"]["signature"] ==
            "0x20b06e5f3d7ebfefda2a2c32befcee5c8192a4531cf9b1b9fc32405a67d8670600a5c3ad962397cf2d455fc62c9a8e316124ccbeb9a66ed7404472de2a1d7dd71b"
        )
        assert (response_body["data"]["snet-current-block-number"] ==
                mock_current_block_no.return_value)

    @patch("common.utils.Utils.report_slack")
    @patch("common.blockchain_util.BlockChainUtil.get_current_block_no")
    def test_signature_for_regular_call(self, mock_current_block_no,
                                        mock_report_slack):
        mock_current_block_no.return_value = 6521925
        response = lambda_handler.request_handler(
            event=self.signature_for_regular_call, context=None)
        assert response["statusCode"] == 200
        response_body = json.loads(response["body"])
        assert response_body["status"] == "success"
        assert (
            response_body["data"]["snet-payment-channel-signature-bin"] ==
            "0x1577fa1caac593525fa79df3afed68079df4e936ebf9fa21411e07d935f57d1007d050a40aff319932a42a8fb713e5a2e3bd9d0c3f1c6d26cff88fceea4a6f991b"
        )
        assert response_body["data"]["snet-payment-type"] == "escrow"
        assert response_body["data"]["snet-payment-channel-id"] == 1
        assert response_body["data"]["snet-payment-channel-nonce"] == 6487832
        assert response_body["data"]["snet-payment-channel-amount"] == 1
        assert (response_body["data"]["snet-current-block-number"] ==
                mock_current_block_no.return_value)


if __name__ == "__main__":
    unittest.main()
