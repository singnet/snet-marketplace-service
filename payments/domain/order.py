import uuid
from datetime import datetime

from payments.domain.paypal_payment import PaypalPayment


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
        if payment_method == "paypal":

            payment = PaypalPayment(
                payment_id=str(uuid.uuid1()),
                amount=amount,
                currency=currency,
                payment_details={
                    "payment_method": payment_method
                },
                payment_status="pending",
                created_at=datetime.utcnow()
            )

            payment_response = payment.initiate_payment(self.get_order_id())
            self._payments.append(payment)
        else:
            raise Exception("Invalid payment gateway")
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
        if payment_method == "paypal":
            payment = self.get_payment(payment_id)
            if not payment.execute_transaction(paid_payment_details):
                raise Exception("Failed payment execution")
        else:
            raise Exception("Invalid payment gateway")
        return payment

    def cancel_payment(self, payment_id):
        payment = self.get_payment(payment_id)
        payment.set_payment_status("failed")