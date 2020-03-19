from dapp_user.domain.models.user_preference import UserPreference
from dapp_user.domain.models.user import User
from dapp_user.constant import SourceDApp, CommunicationType, PreferenceType
from dapp_user.config import CALLER_REFERENCE
from dapp_user.exceptions import InvalidCallerReferenceException


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

    def parse_user_preference_raw_data(self, user_preference_raw_data):
        preferences = []
        for record in user_preference_raw_data:
            communication_type = record["communication_type"]
            preference_type = record["preference_type"]
            source = record["source"]
            status = record["status"]
            opt_out_reason = record.get("opt_out_reason", None)
            preference = UserPreference(
                communication_type=communication_type, preference_type=preference_type,
                source=source, status=status, opt_out_reason=opt_out_reason)
            preferences.append(preference)
        return preferences

    @staticmethod
    def create_user_domain_model(payload, client_id):
        origin = CALLER_REFERENCE.get(client_id, None)
        if not origin:
            raise InvalidCallerReferenceException()
        return User(
            username=payload["email"],
            name=payload["nickname"],
            email=payload["email"],
            email_verified=int(bool(payload['email_verified'])),
            origin=origin,
            preferences=[]
        )
