from dataclasses import dataclass
from typing import List

from dapp_user.constant import CommunicationType, PreferenceType, SourceDApp, Status


@dataclass(frozen=True)
class UserPreference:
    preference_type: PreferenceType
    communication_type: CommunicationType
    source: SourceDApp
    status: Status
    opt_out_reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "preference_type": self.preference_type.value,
            "communication_type": self.communication_type.value,
            "source": self.source.value,
            "status": self.status.value,
            "opt_out_reason": self.opt_out_reason
        }


def user_preferences_to_dict(user_preferences: List[UserPreference]) -> List[dict]:
    return [user_preference.to_dict() for user_preference in user_preferences]