from typing import List, Sequence, Tuple

from dapp_user.application.schemas import (
    AddOrUpdateUserPreferencesRequest,
    CognitoUserPoolEvent,
    CreateUserServiceReviewRequest,
)
from dapp_user.constant import CommunicationType, PreferenceType, SourceDApp, Status
from dapp_user.domain.models.user import NewUser, User
from dapp_user.domain.models.user_preference import UserPreference
from dapp_user.domain.models.user_service_feedback import UserServiceFeedback
from dapp_user.domain.models.user_service_vote import UserServiceVote
from dapp_user.infrastructure.models import User as UserDB
from dapp_user.infrastructure.models import UserPreference as UserPreferenceDB
from dapp_user.infrastructure.models import UserServiceFeedback as UserServiceFeedbackDB
from dapp_user.infrastructure.models import UserServiceVote as UserServiceVoteDB


class UserFactory:
    @staticmethod
    def user_preferences_from_request(request: AddOrUpdateUserPreferencesRequest) -> List[UserPreference]:
        user_preferences = []

        for user_preference_payload in request.user_preferences:
            user_preferences.append(
                UserPreference(
                    preference_type=user_preference_payload.preference_type,
                    communication_type=user_preference_payload.communication_type,
                    source=user_preference_payload.source,
                    status=user_preference_payload.status,
                    opt_out_reason=user_preference_payload.opt_out_reason
                )
            )

        return user_preferences

    @staticmethod
    def user_preference_from_db_model(user_preference_db: UserPreferenceDB) -> UserPreference:
        return UserPreference(
            preference_type=PreferenceType(user_preference_db.preference_type),
            communication_type=CommunicationType(user_preference_db.communication_type),
            source=SourceDApp(user_preference_db.source),
            status=Status(user_preference_db.status),
            opt_out_reason=user_preference_db.opt_out_reason
        )

    @staticmethod
    def user_preferences_from_db_model(user_preferences_db: Sequence[UserPreferenceDB]) -> List[UserPreference]:
        return [UserFactory.user_preference_from_db_model(up) for up in user_preferences_db]

    @staticmethod
    def user_service_feedback_from_db_model(user_feedback_db: UserServiceFeedbackDB) -> UserServiceFeedback:
        return UserServiceFeedback(
            user_row_id=user_feedback_db.user_row_id,
            org_id=user_feedback_db.org_id,
            service_id=user_feedback_db.service_id,
            comment=user_feedback_db.comment,
        )

    @staticmethod
    def user_vote_from_db_model(user_vote_db: UserServiceVoteDB) -> UserServiceVote:
        return UserServiceVote(
            user_row_id=user_vote_db.user_row_id,
            org_id=user_vote_db.org_id,
            service_id=user_vote_db.service_id,
            rating=user_vote_db.rating
        )

    @staticmethod
    def user_vote_feedback_from_request(create_review_request: CreateUserServiceReviewRequest) -> Tuple[UserServiceVote, UserServiceFeedback]:
        user_vote = UserServiceVote(
            user_row_id=create_review_request.user_row_id,
            org_id=create_review_request.org_id,
            service_id=create_review_request.service_id,
            rating=create_review_request.user_rating
        )

        user_feedback = UserServiceFeedback(
            user_row_id=create_review_request.user_row_id,
            org_id=create_review_request.org_id,
            service_id=create_review_request.service_id,
            comment=create_review_request.comment
        )

        return user_vote, user_feedback

    @staticmethod
    def user_from_cognito_request(event: CognitoUserPoolEvent) -> NewUser:
        return NewUser(
            account_id=event.request.user_attributes.sub,
            username=event.request.user_attributes.email,
            name=event.request.user_attributes.nickname,
            email=event.request.user_attributes.email,
            email_verified=event.request.user_attributes.email_verified,
            origin=event.caller_context.origin,
        )

    @staticmethod
    def user_from_db_model(user_db: UserDB) -> User:
        return User(
            row_id=user_db.row_id,
            account_id=user_db.account_id,
            username=user_db.username,
            name=user_db.name,
            email=user_db.email,
            email_verified=bool(user_db.email_verified),
            origin="origin",
        )
