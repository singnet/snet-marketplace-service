from dapp_user.domain.models.user_preference import UserPreference
from dapp_user.constant import SourceDApp, CommunicationType, PreferenceType


class UserFactory:

    @staticmethod
    def parse_raw_user_preference_data(payload):
        user_preference_list = []
        for record in payload:
            communication_type = getattr(CommunicationType, record["communication_type"].upper()).value
            preference_type = getattr(PreferenceType, record["preference_type"].upper()).value
            source = getattr(SourceDApp, record["source"].upper()).value
            status = record["status"]
            opt_out_reason = record.get("opt_out_reason", None)
            user_preference = UserPreference(
                communication_type=communication_type, preference_type=preference_type,
                source=source, status=status, opt_out_reason=opt_out_reason)
            user_preference_list.append(user_preference)
        return user_preference_list
