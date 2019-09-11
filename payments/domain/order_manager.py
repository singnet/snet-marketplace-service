# this is port to accept different kinf of request from different application
class OrderManager(object):

    def create_order(self, amount, agi, username):
        pass

    def create_payment(self, order, payment_details):
        pass

    def execute_payment_for_order(self, order_id, payment_id, payer_id, payment_gateway):
        pass
