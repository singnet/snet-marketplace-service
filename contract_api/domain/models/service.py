from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewServiceDomain:
    org_id: str
    service_id: str
    hash_uri: str
    is_curated: bool


@dataclass
class ServiceDomain(NewServiceDomain):
    row_id: int
    service_path: str
    service_email: str
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "service_path": self.service_path,
            "hash_uri": self.hash_uri,
            "is_curated": self.is_curated,
            "service_email": self.service_email,
        }

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
        }
