import unittest
from unittest.mock import patch, Mock
from payments.domain.paypal_payment import PaypalPayment


class TestPaypal(unittest.TestCase):

    @patch("paypalrestsdk.Payment", return_value=Mock(links=[Mock(rel="approval_url", href="url")],
                                                      id="PAYID-123", create=Mock(return_value=True)))
    @patch("common.boto_utils.BotoUtils.get_ssm_parameter")
    def test_initiate_payment(self, ssm_mock_object, payment_mock_object):
        ssm_mock_object.return_value = "1234"
        payment_id = "123"
        order_id = "order-123"
        amount = 123
        payment_status = ""
        created_at = "2000-01-01 00:00:00"
        payment_details = {}
        item_details = {
            "item": "AGI",
            "quantity": 0.00004,
            "org_id": "snet",
            "service_id": "freecall",
            "group_id": "group-123",
            "recipient": "0x123",
            "order_type": "FUND_CHANNEL"
        }
        currency = "USD"
        response = PaypalPayment(payment_id, amount, currency,
                                 payment_status, created_at, payment_details).initiate_payment(order_id, item_details)
        expected_response = {'payment': {'id': 'PAYID-123', 'payment_url': 'url'}}
        self.assertDictEqual(response, expected_response)

    @patch("paypalrestsdk.Payment.find", return_value=Mock(links=[Mock(rel="approval_url", href="url")],
                                                           id="PAYID-123", execute=Mock(return_value=True)))
    @patch("common.boto_utils.BotoUtils.get_ssm_parameter")
    def test_execute_payment(self, ssm_mock_object, mock_object):
        ssm_mock_object.return_value = "1234"
        payment_id = "123"
        amount = 123
        payment_status = ""
        created_at = "2000-01-01 00:00:00"
        currency = "USD"
        payment_details = {"payment_id": "PAYID-123"}
        assert PaypalPayment(payment_id, amount, currency, payment_status, created_at, payment_details) \
            .execute_transaction({"payer_id": "PAYER-123"})


if __name__ == "__main__":
    TestPaypal()
