from dataclasses import dataclass
from datetime import datetime


@dataclass
class OffchainServiceConfigDomain:
    row_id: int
    org_id: str
    service_id: str
    parameter_name: str
    parameter_value: str

    def to_response(self):
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "parameter_name": self.parameter_name,
            "parameter_value": self.parameter_value
        }

    def to_attribute(self):
        return {
            self.parameter_name: self.parameter_value
        }


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

    @attributes.setter
    def attributes(self, attributes):
        self._attributes = attributes
