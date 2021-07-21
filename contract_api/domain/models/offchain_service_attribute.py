class OffchainServiceAttribute:
    def __init__(self, org_id, service_id, attributes):
        self._org_id = org_id
        self._service_id = service_id
        self._attributes = attributes

    def to_dict(self):
        return {
            "org_id": self._org_id,
            "service_id": self._service_id,
            "attributes": self._attributes
        }

    @property
    def org_id(self):
        return self._org_id

    @property
    def service_id(self):
        return self._service_id

    @property
    def attributes(self):
        return self._attributes
