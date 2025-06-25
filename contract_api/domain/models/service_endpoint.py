from dataclasses import dataclass
from datetime import datetime


@dataclass
class ServiceEndpointDomain:
    row_id: str
    service_row_id: str
    org_id: str
    service_id: str
    group_id: str
    endpoint: str
    is_available: bool
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