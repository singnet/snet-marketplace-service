class OffchainServiceConfig:
    def __init__(self, org_uuid, service_uuid, configs):
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._configs = configs

    @property
    def org_uuid(self):
        return self._org_uuid

    @property
    def service_uuid(self):
        return self._service_uuid

    @property
    def configs(self):
        return self._configs
