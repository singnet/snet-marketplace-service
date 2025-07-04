from typing import List, Tuple

from common.utils import chunked
from dapp_user.constant import Status
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
from dapp_user.infrastructure.repositories.exceptions import (
    FeedbackAlreadyExistsException,
    UserAlreadyExistsException,
    UserNotFoundException,
    VoteAlreadyExistsException,
)
from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class UserRepository:
    def update_user_preferences(
        self, session: Session, user_preferences: List[UserPreferenceDomain], user_row_id: int
    ) -> List[str]:
        statuses: List[str] = []

        for preference in user_preferences:
            query = select(UserPreference).where(
                UserPreference.user_row_id == user_row_id,
                UserPreference.preference_type == preference.preference_type.value,
                UserPreference.communication_type == preference.communication_type.value,
                UserPreference.source == preference.source.value,
            )

            result = session.execute(query)
            existing_preference = result.scalar_one_or_none()
            if existing_preference:
                existing_preference.status = preference.status == Status.ENABLED
                existing_preference.opt_out_reason = preference.opt_out_reason
            else:
                new_preference = UserPreference(
                    user_row_id=user_row_id,
                    preference_type=preference.preference_type.value,
                    communication_type=preference.communication_type.value,
                    source=preference.source.value,
                    opt_out_reason=preference.opt_out_reason,
                    status=preference.status == Status.ENABLED,
                )
                session.add(new_preference)

            statuses.append(preference.status.value)

        return statuses

    def get_user(self, session: Session, username: str) -> UserDomain:
        query = select(User).where(User.username == username).limit(1)
        result = session.execute(query)
        user_db = result.scalar_one_or_none()
        if user_db is None:
            raise UserNotFoundException(username=username)
        return UserFactory.user_from_db_model(user_db)

    def update_user(self, session: Session, username: str, email_alerts: bool) -> None:
        try:
            query = update(User).where(User.username == username).values(email_alerts=email_alerts)
            session.execute(query)
        except IntegrityError:
            raise UserNotFoundException(username=username)

    def get_user_preferences(self, session: Session, username: str) -> List[UserPreferenceDomain]:
        query = (
            select(UserPreference)
            .join(User, User.row_id == UserPreference.user_row_id)
            .where(User.username == username)
        )
        result = session.execute(query)
        user_preference_db = result.scalars().all()

        return UserFactory.user_preferences_from_db_model(user_preference_db)

    def delete_user(self, session: Session, username: str):
        query = delete(User).where(User.username == username)
        result = session.execute(query)
        if result.rowcount == 0:
            raise UserNotFoundException(username=username)

    def batch_insert_users(
        self,
        session: Session,
        users: List[NewUserDomain],
        batch_size: int = 100,
    ):
        if not users:
            return

        for batch in chunked(users, batch_size):
            user_dicts = [
                {
                    "account_id": user.account_id,
                    "username": user.username,
                    "name": user.name,
                    "email": user.email,
                    "email_verified": user.email_verified,
                    "email_alerts": user.email_alerts,
                    "status": user.status,
                    "is_terms_accepted": user.is_terms_accepted,
                }
                for user in batch
            ]

            query = insert(User).values(user_dicts)

            query = query.on_duplicate_key_update(
                name=query.inserted.name,
                email=query.inserted.email,  # no-op
            )

            session.execute(query)

    def insert_user(self, session: Session, user: UserDomain | NewUserDomain):
        try:
            query = insert(User).values(
                username=user.email,
                account_id=user.account_id,
                name=user.name,
                email=user.email,
                email_verified=user.email_verified,
                email_alerts=user.email_alerts,
                status=user.email_verified,
                is_terms_accepted=user.is_terms_accepted,
            )

            session.execute(query)
        except IntegrityError:
            raise UserAlreadyExistsException(username=user.email)

    def __update_or_set_user_vote(self, session: Session, user_vote: UserServiceVoteDomain) -> None:
        query = select(UserServiceVote).where(
            UserServiceVote.row_id == user_vote.user_row_id,
            UserServiceVote.org_id == user_vote.org_id,
            UserServiceVote.service_id == user_vote.service_id,
        )
        vote = session.execute(query).scalar_one_or_none()
        if vote:
            vote.rating = user_vote.rating
        else:
            new_vote = UserServiceVote(
                user_row_id=user_vote.user_row_id,
                org_id=user_vote.org_id,
                service_id=user_vote.service_id,
                rating=user_vote.rating,
            )
            session.add(new_vote)

    def __set_user_feedback(
        self, session: Session, user_feedback: UserServiceFeedbackDomain
    ) -> None:
        feedback = UserServiceFeedback(
            user_row_id=user_feedback.user_row_id,
            org_id=user_feedback.org_id,
            service_id=user_feedback.service_id,
            comment=user_feedback.comment,
        )
        session.add(feedback)

    def __aggregate_service_rating(
        self, session: Session, org_id: str, service_id: str
    ) -> Tuple[float, int]:
        agg_stmt = select(
            func.avg(UserServiceVote.rating).label("avg_rating"),
            func.count(UserServiceVote.rating).label("total_rated"),
        ).where(
            UserServiceVote.org_id == org_id,
            UserServiceVote.service_id == service_id,
            UserServiceVote.rating.isnot(None),
        )
        result = session.execute(agg_stmt).one()
        avg_rating, total_rated = result
        return avg_rating or 0.0, total_rated

    def submit_user_review(
        self,
        session: Session,
        user_vote: UserServiceVoteDomain,
        user_feedback: UserServiceFeedbackDomain | None,
    ) -> Tuple[float, int]:
        try:
            self.__update_or_set_user_vote(session, user_vote)
        except IntegrityError:
            raise VoteAlreadyExistsException()

        if user_feedback is not None:
            try:
                self.__set_user_feedback(session, user_feedback)
            except IntegrityError:
                raise FeedbackAlreadyExistsException()

        avg_rating, total_rated = self.__aggregate_service_rating(
            session=session,
            org_id=user_vote.org_id,
            service_id=user_vote.service_id,
        )
        return avg_rating, total_rated

    def get_user_service_vote_and_feedback(
        self, session: Session, username: str, org_id: str, service_id: str
    ) -> Tuple[UserServiceVoteDomain | None, UserServiceFeedbackDomain | None]:
        print("testest")

        query = (
            select(UserServiceFeedback, UserServiceVote)
            .join_from(UserServiceFeedback, User, UserServiceFeedback.user_row_id == User.row_id)
            .join_from(
                UserServiceFeedback,
                UserServiceVote,
                and_(
                    UserServiceVote.user_row_id == User.row_id,
                    UserServiceVote.org_id == UserServiceFeedback.org_id,
                    UserServiceVote.service_id == UserServiceFeedback.service_id,
                ),
            )
            .where(
                and_(
                    User.username == username,
                    UserServiceFeedback.org_id == org_id,
                    UserServiceFeedback.service_id == service_id,
                )
            )
        )

        print("fasfdsf")

        result = session.execute(query).one_or_none()

        print(result)

        if result:
            user_service_feedback_db, user_service_vote_db = result
            print(user_service_feedback_db, user_service_vote_db)
        else:
            user_service_feedback_db = user_service_vote_db = None

        return (
            UserFactory().user_service_vote_from_db_model(user_service_vote_db)
            if user_service_vote_db
            else None,
            UserFactory().user_service_feedback_from_db_model(user_service_feedback_db)
            if user_service_feedback_db
            else None,
        )

    def get_user_service_feedback(
        self, session: Session, username: str, org_id: str, service_id: str
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
        result = session.execute(query)
        feedback_db = result.scalar_one_or_none()

        return UserFactory.user_service_feedback_from_db_model(feedback_db) if feedback_db else None

    def insert_user_service_vote(
        self, session: Session, user_vote: UserServiceVoteDomain
    ) -> UserServiceVoteDomain:
        new_vote = UserServiceVote(
            user_row_id=user_vote.user_row_id,
            org_id=user_vote.org_id,
            service_id=user_vote.service_id,
            rating=user_vote.rating,
        )

        session.add(new_vote)

        return UserFactory().user_service_vote_from_db_model(new_vote)

    def insert_user_service_feedback(
        self, session: Session, user_feedback: UserServiceFeedbackDomain
    ) -> UserServiceFeedbackDomain:
        new_feedback = UserServiceFeedback(
            user_row_id=user_feedback.user_row_id,
            org_id=user_feedback.org_id,
            service_id=user_feedback.service_id,
            comment=user_feedback.comment,
        )

        session.add(new_feedback)

        return UserFactory.user_service_feedback_from_db_model(new_feedback)

    def get_user_service_vote(
        self, session: Session, user_row_id: int, org_id: str, service_id: str
    ) -> UserServiceVoteDomain | None:
        query = select(UserServiceVote).where(
            UserServiceVote.user_row_id == user_row_id,
            UserServiceVote.org_id == org_id,
            UserServiceVote.service_id == service_id,
        )
        result = session.execute(query)

        user_service_vote_db = result.scalar_one_or_none()

        return (
            UserFactory().user_service_vote_from_db_model(user_service_vote_db)
            if user_service_vote_db
            else None
        )
