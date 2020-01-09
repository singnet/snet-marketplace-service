from dapp_user.constant import CommunicationType
from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.infrastructure.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.user_factory = UserFactory()
        self.user_repo = UserRepository()

    def add_or_update_user_preference(self, payload, username):
        user_preference = self.user_factory.parse_raw_user_preference_data(payload=payload)
        if user_preference.status and user_preference.opt_out_reason is not None:
            raise Exception("Invalid Payload.")
        user_data = self.user_repo.get_user_data_for_given_username(username=username)
        if len(user_data) == 0:
            raise Exception("User is not registered.")
        if user_preference.status is False:
            response = self.user_repo.disable_preference(
                user_preference=user_preference, user_row_id=user_data[0]["row_id"])
        else:
            response = self.user_repo.enable_preference(
                user_preference=user_preference, user_row_id=user_data[0]["row_id"])
        return "success"
