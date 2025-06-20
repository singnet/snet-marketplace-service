from dataclasses import dataclass


@dataclass(frozen=True)
class UserServiceFeedback:
    user_row_id: int
    org_id: str
    service_id: str
    comment: str

    def to_dict(self) -> dict:
        return {
            "user_row_id": self.user_row_id,
            "org_id": self.org_id,
            "service_id": self.service_id,
            "comment": self.comment,
        }
