from dapp_user.domain.models.user_preference import UserPreference
from dapp_user.constant import SourceDApp, CommunicationType, PreferenceType


class UserFactory:

    @staticmethod
    def parse_raw_user_preference_data(payload):
        communication_type = getattr(CommunicationType, payload["communication_type"].upper()).value
        preference_type = getattr(PreferenceType, payload["preference_type"].upper()).value
        source = getattr(SourceDApp, payload["source"].upper()).value
        status = payload["status"]
        opt_out_reason = payload.get("opt_out_reason", None)
        user_preference = UserPreference(
            communication_type=communication_type, preference_type=preference_type,
            source=source, status=status, opt_out_reason=opt_out_reason)
        return user_preference
