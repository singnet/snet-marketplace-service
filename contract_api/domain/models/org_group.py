from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewOrgGroupDomain:
    org_id: str
    group_id: str
    group_name: str
    payment: dict


@dataclass
class OrgGroupDomain(NewOrgGroupDomain):
    row_id: int
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "payment": self.payment,
        }

    def to_short_response(self) -> dict:
        return {
            "groupId": self.group_id,
            "groupName": self.group_name,
            "payment": self.payment,
        }