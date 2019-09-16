import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock
from payments.domain.paypal_payment import PaypalPayment


class TestPaypal(unittest.TestCase):

    @patch("paypalrestsdk.Payment", return_value=Mock(links=[Mock(rel="approval_url", href="url")],
                                                      id="PAYID-123", create=Mock(return_value=True)))
    def test_initiate_payment(self, mock_object):
        payment_id = "123"
        amount = 123
        payment_status = ""
        created_at = "2000-01-01 00:00:00"
        payment_details = {}
        response = PaypalPayment(payment_id, amount, payment_status, created_at, payment_details).initiate_payment()
        expected_response = {'payment': {'id': 'PAYID-123', 'payment_url': 'url'}}
        self.assertDictEqual(response, expected_response)

    @patch("paypalrestsdk.Payment.find", return_value=Mock(links=[Mock(rel="approval_url", href="url")],
                                                           id="PAYID-123", execute=Mock(return_value=True)))
    def test_execute_payment(self, mock_object):
        payment_id = "123"
        amount = 123
        payment_status = ""
        created_at = "2000-01-01 00:00:00"
        payment_details = {"payment_id": "PAYID-123"}
        assert PaypalPayment(payment_id, amount, payment_status, created_at, payment_details) \
            .execute_transaction({"payer_id": "PAYER-123"})


if __name__ == "__main__":
    TestPaypal()
