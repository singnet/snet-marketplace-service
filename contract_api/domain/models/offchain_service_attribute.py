from typing import Dict
from dataclasses import dataclass

@dataclass
class OffchainServiceAttributeEntityModel:

    org_id: str
    service_id: str
    attributes: Dict[str, str]

    def to_dict(self):
        return {
            "org_id": self._org_id,
            "service_id": self._service_id,
            "attributes": self._attributes
        }
