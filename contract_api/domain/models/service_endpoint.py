from dataclasses import dataclass
from datetime import datetime

@dataclass
class NewServiceEndpointDomain:
    service_row_id: str
    org_id: str
    service_id: str
    group_id: str
    endpoint: str
    is_available: bool


@dataclass
class ServiceEndpointDomain(NewServiceEndpointDomain):
    row_id: str
    last_check_timestamp: datetime
    next_check_timestamp: datetime
    failed_status_count: int
    created_on: datetime
    updated_on: datetime

    def to_response(self):
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "group_id": self.group_id,
            "endpoint": self.endpoint,
            "is_available": self.is_available,
            "last_check_timestamp": self.last_check_timestamp,
            "next_check_timestamp": self.next_check_timestamp,
            "failed_status_count": self.failed_status_count,
        }

    def to_short_response(self):
        return {
            "endpoint": self.endpoint,
            "isAvailable": self.is_available,
        }