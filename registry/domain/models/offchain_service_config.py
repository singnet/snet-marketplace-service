class OffchainServiceConfig:
    def __init__(self, org_uuid, service_uuid, parameter_name, parameter_value):
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._parameter_name = parameter_name
        self._parameter_value = parameter_value

    def to_dict(self):
        return {
            "org_uuid": self._org_uuid,
            "service_uuid": self._service_uuid,
            "parameter_name": self._parameter_name,
            "parameter_value": self._parameter_value
        }

    @property
    def org_uuid(self):
        return self._org_uuid

    @property
    def service_uuid(self):
        return self._service_uuid

    @property
    def parameter_name(self):
        return self._parameter_name

    @property
    def parameter_value(self):
        return self._parameter_value
