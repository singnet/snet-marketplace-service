from typing import List

from common.exceptions import BadGateway
from common.logger import get_logger
from dapp_user.application.schemas import (
    AddOrUpdateUserPreferencesRequest,
    CognitoUserPoolEvent,
    CreateUserServiceReviewRequest,
    GetUserFeedbackRequest,
    UpdateUserAlertRequest,
)
from dapp_user.constant import Status
from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.domain.interfaces.contract_api_client_interface import AbstractContractAPIClient
from dapp_user.domain.interfaces.wallet_api_client_interface import AbstractWalletsAPIClient
from dapp_user.domain.models.user_preference import user_preferences_to_dict
from dapp_user.exceptions import UserNotFoundHTTPException
from dapp_user.infrastructure.contract_api_client import ContractAPIClient, ContractAPIClientError
from dapp_user.infrastructure.repositories.exceptions import UserNotFoundException
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from dapp_user.infrastructure.wallets_api_client import WalletsAPIClient, WalletsAPIClientError

logger = get_logger(__name__)


class UserService:
    def __init__(
        self,
        wallets_api_client: AbstractWalletsAPIClient | None = None,
        contract_api_client: AbstractContractAPIClient | None = None,
    ):
        self.user_factory = UserFactory()
        self.user_repo = UserRepository()
        self.wallets_api_client = wallets_api_client or WalletsAPIClient()
        self.contract_api_client = contract_api_client or ContractAPIClient()

    def add_or_update_user_preference(
        self, username: str, request: AddOrUpdateUserPreferencesRequest
    ) -> List[str]:
        user_preference_list = self.user_factory.user_preferences_from_request(request=request)

        try:
            user = self.user_repo.get_user(username=username)
        except UserNotFoundException:
            raise UserNotFoundHTTPException(username)

        response = []

        for user_preference in user_preference_list:
            if user_preference.status == Status.DISABLED:
                self.user_repo.disable_preference(
                    user_preference=user_preference, user_row_id=user.row_id
                )
                response.append(user_preference.status.value)
            else:
                self.user_repo.enable_preference(
                    user_preference=user_preference, user_row_id=user.row_id
                )
                response.append(user_preference.status.value)

        return response

    def get_user(self, username: str) -> dict:
        try:
            user = self.user_repo.get_user(username=username)
        except UserNotFoundException:
            raise UserNotFoundHTTPException(username)
        return user.to_response()

    def get_user_preferences(self, username: str) -> List[dict]:
        user_preferences = self.user_repo.get_user_preferences(username=username)
        return user_preferences_to_dict(user_preferences)

    def delete_user(self, username):
        #: TODO think about rollback or distributed transaction if unlink wallet fails (saga pattern)
        try:
            self.user_repo.delete_user(username)
        except UserNotFoundException:
            raise UserNotFoundHTTPException(username)

        try:
            self.wallets_api_client.delete_user_wallet(username=username)
        except WalletsAPIClientError as e:
            msg = f"Failed to delete user wallet for {username}: {str(e)}"
            logger.error(msg)
            raise BadGateway(msg)

    def register_user(self, request: CognitoUserPoolEvent) -> dict:
        new_user = self.user_factory.user_from_cognito_request(event=request)
        self.user_repo.insert_user(user=new_user)
        return new_user.to_dict()

    def update_user_alerts(self, username: str, request: UpdateUserAlertRequest):
        try:
            self.user_repo.update_user_alerts(
                username=username,
                email_alerts=request.email_alerts,
                is_terms_accepted=request.is_terms_accepted,
            )
        except UserNotFoundException as e:
            logger.error(f"User not found: {e}")
            raise UserNotFoundHTTPException(f"User {username} not found")

    def get_user_service_review(self, username: str, request: GetUserFeedbackRequest) -> dict:
        user_service_vote, user_service_feedback = self.user_repo.get_user_service_vote_and_feedback(
            username=username,
            org_id=request.org_id,
            service_id=request.service_id
        )

        response = {
            "rating": user_service_vote.rating if user_service_vote else None,
            "comment": user_service_feedback.comment if user_service_feedback else None
        }

        return response


    def create_user_review(self, request: CreateUserServiceReviewRequest) -> None:
        user_vote, user_feedback = self.user_factory.user_vote_feedback_from_request(
            create_feedback_request=request
        )
        #: TODO think about rollback or distributed transaction if update service rating fails (saga pattern)
        rating, total_users_rated = self.user_repo.submit_user_feedback(
            user_vote=user_vote, user_feedback=user_feedback
        )
        try:
            self.contract_api_client.update_service_rating(
                org_id=user_vote.org_id,
                service_id=user_vote.service_id,
                rating=rating,
                total_users_rated=total_users_rated,
            )
        except ContractAPIClientError as e:
            msg = f"Failed to update service rating for {user_vote.org_id}/{user_vote.service_id}: {str(e)}"
            logger.error(msg)
            raise BadGateway(msg)
