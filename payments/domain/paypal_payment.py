import paypalrestsdk

from payments.domain.payment import Payment
from payments.settings import MODE, PAYPAL_CLIENT, PAYPAL_SECRET, PAYMENT_CANCEL_URL, PAYMENT_RETURN_URL


class PaypalPayment(Payment):

    def __init__(self, payment_id, amount, payment_status, created_at, payment_details):
        super().__init__(payment_id, amount, payment_status, created_at, payment_details)
        self.payee_client_api = paypalrestsdk.Api({
          'mode': MODE,
          'client_id': PAYPAL_CLIENT,
          'client_secret': PAYPAL_SECRET}
        )

    def initiate_payment(self):
        paypal_payload = self.get_paypal_payload()
        payment = paypalrestsdk.Payment(paypal_payload, api=self.payee_client_api)

        if not payment.create():
            raise Exception("Payment failed to create")

        approval_url = ""

        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)

        if len(approval_url) == 0:
            raise Exception("Payment link not found")

        self._payment_details["payment_id"] = payment.id

        response_payload = {
            "payment": {
                "id": payment.id,
                "payment_url": approval_url
            }
        }

        return response_payload

    def execute_transaction(self, paid_payment_details):
        paypal_payment_id = self._payment_details["payment_id"]
        payer_id = paid_payment_details["payer_id"]
        payment = paypalrestsdk.Payment.find(paypal_payment_id, api=self.payee_client_api)

        if payment.execute({"payer_id": payer_id}):
            self._payment_status = 'success'
            return True
        else:
            self._payment_status = 'failed'
            return False

    def get_paypal_payload(self):
        paypal_payload = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": PAYMENT_RETURN_URL,
                "cancel_url": PAYMENT_CANCEL_URL
            },
            "transactions": [
                {
                    "item_list": {
                        "items": [
                            {
                                "name": "item",
                                "sku": "item",
                                "price": self._amount,
                                "currency": "USD",
                                "quantity": 1
                            }
                        ]
                    },
                    "amount": {
                        "total": self._amount,
                        "currency": "USD"
                    },
                    "description": "This is the payment transaction description."
                }
            ]
        }
        return paypal_payload
