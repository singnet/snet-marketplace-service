# An order have multiplr payment and multiple refund in future
class Order(object):

    def __init__(self, amount, order_id):
        self._order_id = order_id
        self._payments = []
        self._amount = amount

    def add_payment(self, payment_details={}):
        pass

    def update_payment(self, payment_id, status):
        pass


class PayPalOrder(Order):

    def __init__(self, amount, order_id):
        pass

    def execute_payment(self, payment_id):
        # paypal logic of executing payment
        pass
