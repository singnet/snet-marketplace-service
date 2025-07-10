from dataclasses import dataclass
from datetime import datetime

from contract_api.domain.models.base_domain import BaseDomain


@dataclass
class NewServiceEndpointDomain:
    service_row_id: int
    org_id: str
    service_id: str
    group_id: str
    endpoint: str
    is_available: bool
    last_check_timestamp: datetime


@dataclass
class ServiceEndpointDomain(NewServiceEndpointDomain, BaseDomain):
    next_check_timestamp: datetime
    failed_status_count: int

    def to_short_response(self):
        return {
            "endpoint": self.endpoint,
            "isAvailable": self.is_available,
        }