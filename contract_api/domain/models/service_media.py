from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewServiceMediaDomain:
    service_row_id: int
    org_id: str
    service_id: str
    url: str
    order: int
    file_type: str
    asset_type: str
    alt_text: str
    hash_uri: str


@dataclass
class ServiceMediaDomain(NewServiceMediaDomain):
    row_id: str
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "url": self.url,
            "order": self.order,
            "file_type": self.file_type,
            "asset_type": self.asset_type,
            "alt_text": self.alt_text,
            "hash_uri": self.hash_uri,
        }

    def to_short_response(self) -> dict:
        return {
            "url": self.url,
            "assetType": self.asset_type,
        }
