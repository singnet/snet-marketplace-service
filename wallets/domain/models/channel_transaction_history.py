
class ChannelTransactionHistoryModel:
    def __init__(self, order_id, amount, currency, type, address, recipient, signature, org_id, group_id,
                 request_parameters, transaction_hash,
                 status):
        self._order_id = order_id
        self._amount = amount
        self._currency = currency
        self._type = type
        self._address = address
        self._recipient = recipient
        self._signature = signature
        self._org_id = org_id
        self._group_id = group_id
        self._request_parameters = request_parameters
        self._transaction_hash = transaction_hash
        self._status = status

    def to_dict(self):
        return {
            "order_id": self._order_id,
            "amount": self._amount,
            "currency": self._currency,
            "type": self._type,
            "address": self._address,
            "recipient": self._recipient,
            "signature": self._signature,
            "org_id": self._org_id,
            "group_id": self._group_id,
            "request_parameters": self._request_parameters,
            "transaction_hash": self._transaction_hash,
            "status": self._status
        }

    @property
    def order_id(self):
        return self._order_id

    @property
    def amount(self):
        return self._amount

    @property
    def currency(self):
        return self._currency

    @property
    def type(self):
        return self._type

    @property
    def address(self):
        return self._address

    @property
    def recipient(self):
        return self._recipient

    @property
    def signature(self):
        return self._signature

    @property
    def org_id(self):
        return self._org_id

    @property
    def group_id(self):
        return self._group_id

    @property
    def request_parameters(self):
        return self._request_parameters

    @property
    def transaction_hash(self):
        return self._transaction_hash

    @property
    def status(self):
        return self._status

    @order_id.setter
    def order_id(self, order_id):
        self._order_id = order_id

    @amount.setter
    def amount(self, amount):
        self._amount = amount

    @currency.setter
    def currency(self, currency):
        self._currency = currency

    @type.setter
    def type(self, type):
        self._type = type

    @address.setter
    def address(self, address):
        self._address = address

    @recipient.setter
    def recipient(self, recipient):
        self._recipient = recipient

    @signature.setter
    def signature(self, signature):
        self._signature = signature

    @org_id.setter
    def org_id(self, org_id):
        self._org_id = org_id

    @group_id.setter
    def group_id(self, group_id):
        self._group_id = group_id

    @request_parameters.setter
    def request_parameters(self, request_parameters):
        self._request_parameters = request_parameters

    @transaction_hash.setter
    def transaction_hash(self, transaction_hash):
        self._transaction_hash = transaction_hash

    @status.setter
    def status(self, status):
        self._status = status