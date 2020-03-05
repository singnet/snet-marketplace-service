import uuid

from datetime import datetime
from common.logger import get_logger
from common.constant import PaymentStatus, PAYMENT_METHOD_PAYPAL
from payments.domain.paypal_payment import PaypalPayment

logger = get_logger(__name__)


class Order(object):

    def __init__(self):
        self._order_id = None
        self._payments = None
        self._amount = None
        self._item_details = None
        self._username = None
        self._currency = None

    def __init__(self, order_id, amount, currency, item_details, username, payments):
        self._order_id = order_id
        self._payments = payments
        self._amount = amount
        self._item_details = item_details
        self._username = username
        self._currency = currency

    def get_order_id(self):
        return self._order_id

    def get_username(self):
        return self._username

    def get_currency(self):
        return self._currency

    def get_amount(self):
        return self._amount

    def get_item_details(self):
        return self._item_details

    def create_payment(self, amount, currency, payment_method):
        logger.info(f"Initiating payment against order: {self._order_id}, payment_method: {payment_method}")
        if payment_method == PAYMENT_METHOD_PAYPAL:

            payment = PaypalPayment(
                payment_id=str(uuid.uuid1()),
                amount=amount,
                currency=currency,
                payment_details={
                    "payment_method": payment_method
                },
                payment_status=PaymentStatus.PENDING,
                created_at=datetime.utcnow()
            )

            payment_response = payment.initiate_payment(self.get_order_id(), self.get_item_details())
            self._payments.append(payment)
        else:
            raise Exception(f"Invalid payment method: {payment_method}")
        return {
            "payment_object": payment,
            "payment": payment_response["payment"]
        }

    def get_payment(self, payment_id):
        for payment in self._payments:
            if payment.get_payment_id() == payment_id:
                return payment
        return None

    def execute_payment(self, payment_id, paid_payment_details, payment_method):
        logger.info(f"Executing payment {payment_id} using {payment_method}")
        if payment_method == PAYMENT_METHOD_PAYPAL:
            payment = self.get_payment(payment_id)
            if not payment.execute_transaction(paid_payment_details):
                raise Exception("Failed payment execution")
        else:
            raise Exception(f"Invalid payment gateway {payment_method}")
        return payment

    def cancel_payment(self, payment_id):
        logger.info(f"Canceling payment {payment_id}")
        payment = self.get_payment(payment_id)

        if payment.get_payment_status() == PaymentStatus.SUCCESS:
            raise Exception(f"Payment {payment_id} is already in success status")
        elif payment.get_payment_status() == PaymentStatus.FAILED:
            raise Exception(f"Payment {payment_id} is already in failed status")

        payment.set_payment_status(PaymentStatus.FAILED)
        logger.info(f"Payment status set to \"failed\" for payment_id {payment_id}")
