from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OrgGroupDomain:
    row_id: int
    org_id: str
    group_id: str
    group_name: str
    payment: dict
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "payment": self.payment,
        }