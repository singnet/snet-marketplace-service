from typing import List, Tuple

from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.domain.models.user import NewUser as NewUserDomain
from dapp_user.domain.models.user import User as UserDomain
from dapp_user.domain.models.user_preference import UserPreference as UserPreferenceDomain
from dapp_user.domain.models.user_service_feedback import (
    UserServiceFeedback as UserServiceFeedbackDomain,
)
from dapp_user.domain.models.user_service_vote import UserServiceVote as UserServiceVoteDomain
from dapp_user.infrastructure.models import (
    User,
    UserPreference,
    UserServiceFeedback,
    UserServiceVote,
)
from dapp_user.infrastructure.repositories.base_repository import BaseRepository
from dapp_user.infrastructure.repositories.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    UserPreferenceAlreadyExistsException,
    UserPreferenceNotFoundException,
)
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError


class UserRepository(BaseRepository):
    @BaseRepository.write_ops
    def enable_preference(self, user_preference: UserPreferenceDomain, user_row_id: int):
        try:
            self.session.add(
                UserPreference(
                    user_row_id=user_row_id,
                    preference_type=user_preference.preference_type.value,
                    communication_type=user_preference.communication_type.value,
                    source=user_preference.source.value,
                    opt_out_reason=user_preference.opt_out_reason,
                    status=user_preference.status,
                )
            )
            self.session.commit()
        except IntegrityError:
            raise UserPreferenceAlreadyExistsException(
                user_row_id=user_row_id,
                preference_type=user_preference.preference_type.value,
                communication_type=user_preference.communication_type.value,
                source=user_preference.source.value,
            )

    def get_user(self, username: str) -> UserDomain:
        query = select(User).where(User.username == username).limit(1)
        result = self.session.execute(query)
        user_db = result.scalar_one_or_none()
        if user_db is None:
            raise UserNotFoundException(username=username)
        return UserFactory.user_from_db_model(user_db)

    def update_user_alerts(
        self, username: str, email_alerts: bool, is_terms_accepted: bool
    ) -> None:
        try:
            stmt = (
                update(User)
                .where(User.username == username)
                .values(
                    email_alerts=email_alerts,
                    is_terms_accepted=is_terms_accepted,
                )
            )
            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError:
            raise UserNotFoundException(username=username)

    @BaseRepository.write_ops
    def disable_preference(self, user_preference: UserPreferenceDomain, user_row_id: int):
        try:
            stmt = (
                update(UserPreference)
                .where(
                    UserPreference.user_row_id == user_row_id,
                    UserPreference.preference_type == user_preference.preference_type,
                    UserPreference.communication_type == user_preference.communication_type,
                    UserPreference.source == user_preference.source,
                )
                .values(
                    status=user_preference.status, opt_out_reason=user_preference.opt_out_reason
                )
            )

            self.session.execute(stmt)
            self.session.commit()
        except IntegrityError:
            raise UserPreferenceNotFoundException(user_row_id=user_row_id)

    def get_user_preferences(self, username: str) -> List[UserPreferenceDomain]:
        query = (
            select(UserPreference)
            .join(User, User.row_id == UserPreference.user_row_id)
            .where(User.username == username)
        )
        result = self.session.execute(query)
        user_preference_db = result.scalars().all()

        return UserFactory.user_preferences_from_db_model(user_preference_db)

    @BaseRepository.write_ops
    def delete_user(self, username: str):
        try:
            query = delete(UserPreference).where(User.username == username)
            self.session.execute(query)
            self.session.commit
        except IntegrityError:
            raise UserNotFoundException(username=username)

    @BaseRepository.write_ops
    def insert_user(self, user: UserDomain | NewUserDomain):
        try:
            query = insert(User).values(
                username=user.email,
                account_id=user.account_id,
                name=user.name,
                email=user.email,
                email_verified=user.email_verified,
                email_alerts=user.email_alerts,
                status=user.email_verified,
                request_id=user.request_id,
                request_time_epoch=user.request_time_epoch,
                is_terms_accepted=user.is_terms_accepted,
            )

            self.session.execute(query)
            self.session.commit()
        except IntegrityError:
            raise UserAlreadyExistsException(username=user.email)

    @BaseRepository.write_ops
    def __update_or_set_user_vote(self, user_vote: UserServiceVoteDomain) -> None:
        stmt = select(UserServiceVote).where(
            UserServiceVote.row_id == user_vote.user_row_id,
            UserServiceVote.org_id == user_vote.org_id,
            UserServiceVote.service_id == user_vote.service_id,
        )
        vote = self.session.execute(stmt).scalar_one_or_none()
        if vote:
            vote.rating = user_vote.rating
        else:
            new_vote = UserServiceVote(
                user_row_id=user_vote.user_row_id,
                org_id=user_vote.org_id,
                service_id=user_vote.service_id,
                rating=user_vote.rating,
            )
            self.session.add(new_vote)

    @BaseRepository.write_ops
    def __set_user_feedback(self, user_feedback: UserServiceFeedbackDomain) -> None:
        feedback = UserServiceFeedback(
            user_row_id=user_feedback.user_row_id,
            org_id=user_feedback.org_id,
            service_id=user_feedback.service_id,
            comment=user_feedback.comment,
        )
        self.session.add(feedback)

    def __aggregate_service_rating(self, org_id: str, service_id: str) -> Tuple[float, int]:
        agg_stmt = select(
            func.avg(UserServiceVote.rating).label("avg_rating"),
            func.count(UserServiceVote.rating).label("total_rated"),
        ).where(
            UserServiceVote.org_id == org_id,
            UserServiceVote.service_id == service_id,
            UserServiceVote.rating.isnot(None),
        )
        result = self.session.execute(agg_stmt).one()
        avg_rating, total_rated = result
        return avg_rating or 0.0, total_rated

    def submit_user_review(
        self,
        user_vote: UserServiceVoteDomain,
        user_feedback: UserServiceFeedbackDomain,
    ) -> Tuple[float, int]:
        """
        Atomically sets user vote and feedback, then returns updated aggregated rating info.
        """
        with self.session.begin():
            self.__update_or_set_user_vote(user_vote)
            self.__set_user_feedback(user_feedback)
            avg_rating, total_rated = self.__aggregate_service_rating(
                org_id=user_vote.org_id,
                service_id=user_vote.service_id,
            )
        return avg_rating, total_rated

    def get_user_service_feedback(
        self, username: str, org_id: str, service_id: str
    ) -> UserServiceFeedbackDomain | None:
        query = (
            select(UserServiceFeedback)
            .join(User, User.row_id == UserServiceFeedback.user_row_id)
            .where(
                User.username == username,
                UserServiceFeedback.org_id == org_id,
                UserServiceFeedback.service_id == service_id,
            )
        )
        result = self.session.execute(query)
        feedback_db = result.scalar_one_or_none()

        return UserFactory.user_service_feedback_from_db_model(feedback_db) if feedback_db else None

    def insert_user_service_vote(self, user_vote: UserServiceVoteDomain) -> UserServiceVoteDomain:
        """
        Inserts a new user service vote into the database.
        """
        new_vote = UserServiceVote(
            user_row_id=user_vote.user_row_id,
            org_id=user_vote.org_id,
            service_id=user_vote.service_id,
            rating=user_vote.rating,
        )
        self.session.add(new_vote)
        self.session.commit()
        return UserFactory.user_vote_from_db_model(new_vote)

    def insert_user_service_feedback(
        self, user_feedback: UserServiceFeedbackDomain
    ) -> UserServiceFeedbackDomain:
        new_feedback = UserServiceFeedback(
            user_row_id=user_feedback.user_row_id,
            org_id=user_feedback.org_id,
            service_id=user_feedback.service_id,
            comment=user_feedback.comment,
        )
        self.session.add(new_feedback)
        self.session.commit()
        return UserFactory.user_service_feedback_from_db_model(new_feedback)
