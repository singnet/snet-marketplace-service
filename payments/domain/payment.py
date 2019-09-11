
class Payment(object):

    def __init__(self):
        self._payment_id = None
        self._amount = None
        self._payment_status = None
        self._created_at = None

    def __init__(self, payment_id, amount, payment_status, created_at, payment_details):
        self._payment_id = payment_id
        self._amount = amount
        self._payment_status = payment_status
        self._created_at = created_at
        self._payment_details = payment_details

    def get_payment_status(self):
        return self._payment_status

    def get_payment_id(self):
        return self._payment_id

    def get_amount(self):
        return self._amount

    def get_payment_gateway(self):
        return self._payment_gateway

    def set_payment_status(self, payment_status):
        self._payment_status = payment_status
