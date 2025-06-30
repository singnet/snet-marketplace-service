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
