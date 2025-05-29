import json
from common.boto_utils import BotoUtils
from common.logger import get_logger
from dapp_user.config import DELETE_USER_WALLET_ARN, REGION_NAME
from dapp_user.constant import Status
from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from dapp_user.exceptions import EmailNotVerifiedException

logger = get_logger(__name__)

class UserService:
    def __init__(self):
        self.user_factory = UserFactory()
        self.user_repo = UserRepository()
        self.boto_client = BotoUtils(REGION_NAME)

    def add_or_update_user_preference(self, payload, username):
        user_preference_list = self.user_factory.parse_raw_user_preference_data(payload=payload)
        response = []
        for user_preference in user_preference_list:
            if user_preference.status and user_preference.opt_out_reason is not None:
                raise Exception("Invalid Payload.")
            user_data = self.user_repo.get_user_data_for_given_username(username=username)
            if len(user_data) == 0:
                raise Exception("User is not registered.")
            if user_preference.status is False:
                self.user_repo.disable_preference(
                    user_preference=user_preference, user_row_id=user_data[0]["row_id"])
                response.append(Status.DISABLED.value)
            else:
                self.user_repo.enable_preference(
                    user_preference=user_preference, user_row_id=user_data[0]["row_id"])
                response.append(Status.ENABLED.value)

        return response

    def get_user_preference(self, username):
        user_data = self.user_repo.get_user_data_for_given_username(username=username)
        if len(user_data) == 0:
            raise Exception("User is not registered.")
        user_preference_raw_data = self.user_repo.get_user_preferences(user_row_id=user_data[0]["row_id"])
        preferences = self.user_factory.parse_user_preference_raw_data(user_preference_raw_data)
        return [preference.to_dict() for preference in preferences]

    def delete_user(self, username):
        self.user_repo.delete_user(username)
        self._unlink_wallets_from_user(username)

    def _unlink_wallets_from_user(self, username):
        delete_user_wallet_event = {
            "body": json.dumps({
                "username": username
            })
        }

        delete_user_wallet_response = self.boto_client.invoke_lambda(
            lambda_function_arn=DELETE_USER_WALLET_ARN,
            invocation_type='RequestResponse',
            payload=json.dumps(delete_user_wallet_event)
        )

        logger.info(f"create_channel_response {delete_user_wallet_response}")
        if delete_user_wallet_response["statusCode"] != 201:
            raise Exception(f"Failed to delete user wallet")

    def register_user(self, user_attribute, client_id):
        user = self.user_factory.create_user_domain_model(payload=user_attribute, client_id=client_id)
        if not user.email_verified:
            raise EmailNotVerifiedException()
        return self.user_repo.register_user_data(user)
