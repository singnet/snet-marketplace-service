from dataclasses import dataclass


@dataclass(frozen=True)
class UserServiceVote:
    user_row_id: int
    org_id: str
    service_id: str
    rating: float

    def to_response(self) -> dict:
        return {
            "user_row_id": self.user_row_id,
            "org_id": self.org_id,
            "service_id": self.service_id,
            "rating": self.rating,
        }
