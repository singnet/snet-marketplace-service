from abc import ABC, abstractmethod
from typing import List, Tuple

from dapp_user.domain.models.user import (
    NewUser as NewUserDomain,
)
from dapp_user.domain.models.user import (
    User as UserDomain,
)
from dapp_user.domain.models.user_preference import UserPreference as UserPreferenceDomain
from dapp_user.domain.models.user_service_feedback import (
    UserServiceFeedback as UserServiceFeedbackDomain,
)
from dapp_user.domain.models.user_service_vote import UserServiceVote as UserServiceVoteDomain
from sqlalchemy.orm import Session


class AbstractUserRepository(ABC):
    @abstractmethod
    def get_user(self, session: Session, username: str) -> UserDomain: ...

    @abstractmethod
    def insert_user(self, sessoin: Session, user: NewUserDomain) -> None: ...

    @abstractmethod
    def update_user(self, session: Session, username: str, email_alerts: bool) -> None: ...

    @abstractmethod
    def delete_user(self, session: Session, username: str) -> None: ...

    @abstractmethod
    def batch_insert_users(
        self, session: Session, users: List[NewUserDomain], batch_size: int = 100
    ) -> None: ...

    @abstractmethod
    def get_user_preferences(
        self, session: Session, username: str
    ) -> List[UserPreferenceDomain]: ...

    @abstractmethod
    def update_user_preferences(
        self, session: Session, user_preferences: List[UserPreferenceDomain], user_row_id: int
    ) -> List[str]: ...

    @abstractmethod
    def submit_user_review(
        self,
        session: Session,
        user_vote: UserServiceVoteDomain,
        user_feedback: UserServiceFeedbackDomain | None,
    ) -> Tuple[float, int]: ...

    @abstractmethod
    def get_user_service_vote_and_feedback(
        self,
        session: Session,
        username: str,
        org_id: str,
        service_id: str,
    ) -> Tuple[UserServiceVoteDomain | None, UserServiceFeedbackDomain | None]: ...

    @abstractmethod
    def get_user_service_feedback(
        self,
        session: Session,
        username: str,
        org_id: str,
        service_id: str,
    ) -> UserServiceFeedbackDomain | None: ...

    @abstractmethod
    def get_user_service_vote(
        self,
        session: Session,
        username: str,
        org_id: str,
        service_id: str,
    ) -> UserServiceVoteDomain | None: ...

    @abstractmethod
    def insert_user_service_feedback(
        self, session: Session, user_vote: UserServiceVoteDomain
    ) -> None: ...

    @abstractmethod
    def insert_user_servie_feedback(
        self, session: Session, user_feedback: UserServiceFeedbackDomain
    ) -> None: ...
