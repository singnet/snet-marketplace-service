import paypalrestsdk

from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.constant import PaymentStatus, PAYMENT_METHOD_PAYPAL
from payments.domain.payment import Payment
from payments.config import MODE, PAYPAL_CLIENT, PAYPAL_SECRET, PAYMENT_CANCEL_URL, PAYMENT_RETURN_URL, REGION_NAME

logger = get_logger(__name__)


class PaypalPayment(Payment):

    def __init__(self, payment_id, amount, currency, payment_status, created_at, payment_details):
        super().__init__(payment_id, amount, currency, payment_status, created_at, payment_details)
        self.boto_utils = BotoUtils(region_name=REGION_NAME)

    def initiate_payment(self, order_id, item_details):
        try:
            payee_client_api = paypalrestsdk.Api({
                'mode': MODE,
                'client_id': self.boto_utils.get_ssm_parameter(PAYPAL_CLIENT),
                'client_secret': self.boto_utils.get_ssm_parameter(PAYPAL_SECRET)
            })
        except Exception as e:
            logger.error("Failed to get ssm parameters")
            raise e
        paypal_payload = self.get_paypal_payload(order_id, item_details["org_id"], item_details["service_id"])
        payment = paypalrestsdk.Payment(paypal_payload, api=payee_client_api)

        if not payment.create():
            logger.error(f"Paypal error:{payment.error}")
            raise Exception("Payment failed to create")

        logger.info(f"Paypal payment initiated with paypal_payment_id: {payment.id}")

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
        try:
            payee_client_api = paypalrestsdk.Api({
                'mode': MODE,
                'client_id': self.boto_utils.get_ssm_parameter(PAYPAL_CLIENT),
                'client_secret': self.boto_utils.get_ssm_parameter(PAYPAL_SECRET)
            })
        except Exception as e:
            logger.error("Failed to get ssm parameters")
            raise e
        paypal_payment_id = self._payment_details["payment_id"]
        payer_id = paid_payment_details["payer_id"]
        payment = paypalrestsdk.Payment.find(paypal_payment_id, api=payee_client_api)

        if payment.execute({"payer_id": payer_id}):
            logger.info(f"Paypal payment execution is success for paypal_payment_id:{paypal_payment_id}")
            self._payment_status = PaymentStatus.SUCCESS

            return True
        elif self._payment_status == PaymentStatus.PENDING:
            logger.info(f"Paypal payment execution is failed for paypal_payment_id:{paypal_payment_id}")
            self._payment_status = PaymentStatus.FAILED

        logger.error(payment.error)
        return False

    def get_paypal_payload(self, order_id, org_id, service_id):
        paypal_payload = {
            "intent": "sale",
            "payer": {
                "payment_method": PAYMENT_METHOD_PAYPAL
            },
            "redirect_urls": {
                "return_url": PAYMENT_RETURN_URL.format(org_id, service_id, order_id, self._payment_id),
                "cancel_url": PAYMENT_CANCEL_URL.format(org_id, service_id, order_id, self._payment_id)
            },
            "transactions": [
                {
                    "item_list": {
                        "items": [
                            {
                                "name": "item",
                                "sku": "item",
                                "price": self._amount,
                                "currency": self._currency,
                                "quantity": 1
                            }
                        ]
                    },
                    "amount": {
                        "total": self._amount,
                        "currency": self._currency
                    },
                    "description": ""
                }
            ]
        }
        return paypal_payload
