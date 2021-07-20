class OffchainServiceConfig:
    def __init__(self, org_id, service_id, configs):
        self._org_id = org_id
        self._service_id = service_id
        self._configs = configs

    def to_dict(self):
        return {
            "org_id": self._org_id,
            "service_id": self._service_id,
            "configs": self._configs
        }

    @property
    def org_id(self):
        return self._org_id

    @property
    def service_id(self):
        return self._service_id

    @property
    def configs(self):
        return self._configs
