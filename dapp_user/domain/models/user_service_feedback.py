from dataclasses import dataclass


@dataclass(frozen=True)
class UserServiceFeedback:
    user_row_id: int
    org_id: str
    service_id: str
    comment: str

    def to_response(self) -> dict:
        return {
            "userRowId": self.user_row_id,
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "comment": self.comment,
        }
