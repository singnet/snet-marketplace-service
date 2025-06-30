from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewServiceTagDomain:
    service_row_id: int
    org_id: str
    service_id: str
    tag_name: str


@dataclass
class ServiceTagDomain(NewServiceTagDomain):
    row_id: int
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "tag_name": self.tag_name,
        }
