from dataclasses import dataclass


@dataclass
class ServiceMediaEntityModel:
    
    org_id: str
    service_id: str
    url: str
    order: int
    file_type: str
    asset_type: str
    alt_text: str
    ipfs_url: str

    def to_dict(self):
        return {
            "service_row_id": self._service_row_id,
            "org_id": self._org_id,
            "service_id": self._service_id,
            "url": self._url,
            "order": self._order,
            "file_type": self._file_type,
            "asset_type": self._asset_type,
            "alt_text": self._alt_text
        }
