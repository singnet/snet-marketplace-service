from dataclasses import dataclass
from datetime import datetime


@dataclass
class ServiceDomain:
    row_id: int
    org_id: str
    service_id: str
    service_path: str
    hash_uri: str
    is_curated: bool
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

class Service:
    def __init__(self, org_id, service_id, service_path, hash_uri, is_curated, service_email, service_metadata, row_id=None):
        self._row_id = row_id
        self._org_id = org_id
        self._service_id = service_id
        self._service_path = service_path
        self._hash_uri = hash_uri
        self._is_curated = is_curated
        self._service_email = service_email
        self._service_metadata = service_metadata

    @property
    def org_id(self):
        return self._org_id

    @org_id.setter
    def org_id(self, org_id):
        self._org_id = org_id

    @property
    def service_id(self):
        return self._service_id

    @service_id.setter
    def service_id(self, service_id):
        self._service_id = service_id

    @property
    def service_path(self):
        return self._service_path

    @service_path.setter
    def service_path(self, service_path):
        self._service_path = service_path

    @property
    def hash_uri(self):
        return self._hash_uri

    @hash_uri.setter
    def hash_uri(self, hash_uri):
        self._hash_uri = hash_uri

    @property
    def is_curated(self):
        return self._is_curated

    @is_curated.setter
    def is_curated(self, is_curated):
        self._is_curated = is_curated

    @property
    def service_email(self):
        return self._service_email

    @service_email.setter
    def service_email(self, service_email):
        self._service_email = service_email

    @property
    def service_metadata(self):
        return self._service_metadata

    @service_metadata.setter
    def service_metadata(self, service_metadata):
        self._service_metadata = service_metadata

    @property
    def row_id(self):
        return self._row_id

    @row_id.setter
    def row_id(self, row_id):
        self._row_id = row_id



