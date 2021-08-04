class ChannelTransactionHistory:
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
    def recipent(self):
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