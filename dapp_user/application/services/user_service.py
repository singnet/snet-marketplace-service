from typing import List

from common.exceptions import BadGateway
from common.logger import get_logger
from dapp_user.application.schemas import (
    AddOrUpdateUserPreferencesRequest,
    CognitoUserPoolEvent,
    CreateUserServiceReviewRequest,
    GetUserFeedbackRequest,
    UpdateUserAlertsRequest,
)
from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.domain.interfaces.contract_api_client_interface import AbstractContractAPIClient
from dapp_user.domain.interfaces.user_identity_manager_interface import UserIdentityManager
from dapp_user.domain.interfaces.user_repository_interface import AbstractUserRepository
from dapp_user.domain.interfaces.wallet_api_client_interface import AbstractWalletsAPIClient
from dapp_user.domain.models.user_preference import user_preferences_to_dict
from dapp_user.exceptions import UserNotFoundHTTPException, UserReviewAlreadyExistHTTPException
from dapp_user.infrastructure.cognito_api import CognitoUserManager
from dapp_user.infrastructure.contract_api_client import ContractAPIClient, ContractAPIClientError
from dapp_user.infrastructure.db import DefaultSessionFactory, session_scope
from dapp_user.infrastructure.repositories.exceptions import (
    FeedbackAlreadyExistsException,
    UserNotFoundException,
    VoteAlreadyExistsException,
)
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from dapp_user.infrastructure.wallets_api_client import WalletsAPIClient, WalletsAPIClientError
from dapp_user.settings import settings
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)


class UserService:
    def __init__(
        self,
        session_factory: sessionmaker | None = None,
        user_repository: AbstractUserRepository | None = None,
        wallets_api_client: AbstractWalletsAPIClient | None = None,
        contract_api_client: AbstractContractAPIClient | None = None,
        user_identity_manager: UserIdentityManager | None = None,
    ):
        self.session_factory = session_factory or DefaultSessionFactory
        self.user_repo = user_repository or UserRepository()
        self.wallets_api_client = wallets_api_client or WalletsAPIClient()
        self.contract_api_client = contract_api_client or ContractAPIClient()
        self.user_identity_manager = user_identity_manager or CognitoUserManager(
            settings.aws.cognito_pool
        )

    def add_or_update_user_preference(
        self, username: str, request: AddOrUpdateUserPreferencesRequest
    ) -> List[str]:
        user_preference_list = UserFactory.user_preferences_from_request(request=request)

        try:
            with session_scope(self.session_factory) as session:
                user = self.user_repo.get_user(session, username=username)
                statuses = self.user_repo.update_user_preferences(
                    session, user_preference_list, user.row_id
                )
                return statuses
        except UserNotFoundException:
            raise UserNotFoundHTTPException(username)

    def get_user(self, username: str) -> dict:
        try:
            with session_scope(self.session_factory) as session:
                user = self.user_repo.get_user(session, username=username)
                return user.to_response()
        except UserNotFoundException:
            raise UserNotFoundHTTPException(username)

    def get_user_preferences(self, username: str) -> List[dict]:
        with session_scope(self.session_factory) as session:
            user_preferences = self.user_repo.get_user_preferences(session, username=username)
        return user_preferences_to_dict(user_preferences)

    #: TODO think about rollback or distributed transaction if unlink wallet fails (saga pattern)
    def delete_user(self, username: str) -> None:
        try:
            with session_scope(self.session_factory) as session:
                self.user_repo.delete_user(session, username)
        except UserNotFoundException:
            raise UserNotFoundHTTPException(username)

        try:
            self.wallets_api_client.delete_user_wallet(username=username)
        except WalletsAPIClientError as e:
            msg = f"Failed to delete user wallet for {username}: {str(e)}"
            logger.error(msg)
            raise BadGateway(msg)

    def sync_users(self) -> None:
        users_for_sync = self.user_identity_manager.get_all_users()

        with session_scope(self.session_factory) as session:
            self.user_repo.batch_insert_users(session, users_for_sync)

    def register_user(self, request: CognitoUserPoolEvent) -> dict:
        new_user = UserFactory.user_from_cognito_request(event=request)

        with session_scope(self.session_factory) as session:
            self.user_repo.insert_user(session, user=new_user)

        return new_user.to_dict()

    def update_user(self, username: str, request: UpdateUserAlertsRequest) -> None:
        try:
            with session_scope(self.session_factory) as session:
                self.user_repo.update_user(
                    session=session,
                    username=username,
                    email_alerts=request.email_alerts,
                )
        except UserNotFoundException as e:
            logger.error(f"User not found: {e}")
            raise UserNotFoundHTTPException(f"User {username} not found")

    def get_user_service_review(self, username: str, request: GetUserFeedbackRequest) -> dict:
        with session_scope(self.session_factory) as session:
            user_service_vote, user_service_feedback = (
                self.user_repo.get_user_service_vote_and_feedback(
                    session=session,
                    username=username,
                    org_id=request.org_id,
                    service_id=request.service_id,
                )
            )

        response = {
            "rating": float(user_service_vote.rating) if user_service_vote else None,
            "comment": user_service_feedback.comment if user_service_feedback else None,
        }

        return response

    # TODO think about rollback or distributed transaction if update service rating fails (saga pattern)
    def create_user_review(self, username: str, request: CreateUserServiceReviewRequest) -> None:
        try:
            with session_scope(self.session_factory) as session:
                user = self.user_repo.get_user(session, username=username)

                user_vote, user_feedback = UserFactory.user_vote_feedback_from_request(
                    user_row_id=user.row_id, create_feedback_request=request
                )

                rating, total_users_rated = self.user_repo.submit_user_review(
                    session=session, user_vote=user_vote, user_feedback=user_feedback
                )
        except (VoteAlreadyExistsException, FeedbackAlreadyExistsException):
            raise UserReviewAlreadyExistHTTPException()

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
