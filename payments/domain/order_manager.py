# this is port to accept different kinf of request from different application
class OrderManager(object):
    def create_order(self, amount, payment_gateway):
        pass

    def create_payment(self, order, payment_details):
        pass

    def execute_payment_for_order(self):
        pass
