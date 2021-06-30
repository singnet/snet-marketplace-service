class ServiceState:
    def __init__(self, org_uuid, service_uuid, state, transaction_hash):
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._state = state
        self._transaction_hash = transaction_hash

    def to_dict(self):
        return {
            "org_uuid": self._org_uuid,
            "service_uuid": self._service_uuid,
            "state": self._state,
            "transaction_hash": self._transaction_hash
        }

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def transaction_hash(self):
        return self._transaction_hash

    @transaction_hash.setter
    def transaction_hash(self, transaction_hash):
        self._transaction_hash = transaction_hash

    @property
    def org_uuid(self):
        return self._org_uuid

    @property
    def service_uuid(self):
        return self._service_uuid
