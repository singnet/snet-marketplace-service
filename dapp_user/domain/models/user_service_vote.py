from dataclasses import dataclass


@dataclass(frozen=True)
class UserServiceVote:
    user_row_id: int
    org_id: str
    service_id: str
    rating: float
