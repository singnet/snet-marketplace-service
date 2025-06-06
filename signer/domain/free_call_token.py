from dataclasses import dataclass


@dataclass(frozen=True)
class FreeCallTokenInfoEntity:
    username: str
    organization_id: str
    service_id: str
    group_id: str
    token: bytes
    expiration_block_number: int
