from dataclasses import dataclass
from datetime import datetime


@dataclass
class ServiceGroupDomain:
    row_id: str
    service_row_id: int
    org_id: str
    service_id: str
    group_id: str
    group_name: str
    free_call_signer_address: str
    free_calls: int
    pricing: dict
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "free_call_signer_address": self.free_call_signer_address,
            "free_calls": self.free_calls,
            "pricing": self.pricing,
        }

    def to_short_response(self) -> dict:
        return {
            "groupId": self.group_id,
            "groupName": self.group_name,
            "freeCallSignerAddress": self.free_call_signer_address,
            "freeCalls": self.free_calls,
            "pricing": self.pricing,
        }