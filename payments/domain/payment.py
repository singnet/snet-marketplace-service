
class Payment:

    def __init__(self):
        self._payment_id = None
        self._amount = None
        self._currency = None
        self._payment_status = None
        self._created_at = None
        self._payment_details = {}

    def __init__(self, payment_id, amount, currency, payment_status, created_at, payment_details):
        self._payment_id = payment_id
        self._amount = amount
        self._currency = currency
        self._payment_status = payment_status
        self._created_at = created_at
        self._payment_details = payment_details

    def get_payment_status(self):
        return self._payment_status

    def get_payment_id(self):
        return self._payment_id

    def get_currency(self):
        return self._currency

    def get_amount(self):
        return self._amount

    def get_payment_details(self):
        return self._payment_details

    def set_payment_details(self, payment_details):
        self._payment_details = payment_details

    def get_created_at(self):
        return self._created_at

    def set_payment_status(self, payment_status):
        self._payment_status = payment_status

    def initiate_payment(self, order_id, item_details):
        pass

    def execute_transaction(self, paid_payment_details):
        pass
