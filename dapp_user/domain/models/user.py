from dataclasses import dataclass


@dataclass(frozen=True)
class BaseUser:
    account_id: str
    username: str
    name: str
    email: str
    email_verified: bool
    email_alerts: bool
    status: bool
    request_id: str
    request_time_epoch: str
    is_terms_accepted: bool


@dataclass(frozen=True)
class NewUser(BaseUser):
    def to_dict(self):
        return {
            "account_id": self.account_id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "email_verified": self.email_verified,
        }


@dataclass(frozen=True)
class User(BaseUser):
    row_id: int

    def to_dict(self):
        return {
            "row_id": self.row_id,
            "account_id": self.account_id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "email_verified": int(self.email_verified),
        }
