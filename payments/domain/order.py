# An order have multiplr payment and multiple refund in future
from payments.domain.paypal import initiate_paypal_payment


class Order(object):

    def __init__(self):
        self._order_id = None
        self._payments = None
        self._amount = None
        self._item_details = None
        self._username = None

    def __init__(self, order_id, amount, item_details, username, payments):
        self._order_id = order_id
        self._payments = payments
        self._amount = amount
        self._item_details = item_details
        self._username = username

    def get_order_id(self):
        return self._order_id

    def get_username(self):
        return self._username

    def get_amount(self):
        return self._amount

    def get_item_details(self):
        return self._item_details

    def create_payment(self, amount, payment_method):
        if payment_method == "paypal":
            initiate_paypal_payment(amount)
        else:
            raise Exception("Invalide payment gateway")
        return

    def update_payment(self, payment_id, status):
        pass

    def execute_payment(self, payment_id):
        pass
