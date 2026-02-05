import os
from typing import Callable, Generator, List, Tuple

import pytest
from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.domain.models.user import NewUser
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
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.mysql import MySqlContainer

from alembic import command
from alembic.config import Config

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ALEMBIC_INI_PATH = os.path.join(ROOT_DIR, "alembic.ini")
TEST_USER = "integration@example.com"


@pytest.fixture(scope="session")
def mysql_container():
    """Start a MySQL Docker container for the test session."""
    container = MySqlContainer(
        image="mysql:8.0",
        username="test_user",
        password="test_password",
        dbname="dapp_user_test",
        dialect="pymysql",
    )
    with container as c:
        yield c


@pytest.fixture(scope="session")
def db_engine(mysql_container) -> Engine:
    """Create SQLAlchemy engine connected to the test container."""
    url = mysql_container.get_connection_url()
    return create_engine(url, pool_pre_ping=True)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(mysql_container) -> Generator[None, None, None]:
    """Apply Alembic migrations to the container database, then downgrade after."""
    test_db_url = mysql_container.get_connection_url()

    alembic_cfg = Config(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    command.upgrade(alembic_cfg, "head")

    yield

    alembic_cfg_down = Config(ALEMBIC_INI_PATH)
    alembic_cfg_down.set_main_option("sqlalchemy.url", test_db_url)
    command.downgrade(alembic_cfg_down, "base")


@pytest.fixture(scope="function")
def db_session(db_engine: Engine, apply_migrations) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    connection = db_engine.connect()
    _TestSession = sessionmaker(bind=db_engine)
    session = _TestSession(bind=connection)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        connection.close()


@pytest.fixture(scope="function")
def test_session_factory(db_engine: Engine) -> Callable[[], Session]:
    return sessionmaker(bind=db_engine)


@pytest.fixture
def lambda_event_authorized() -> dict:
    """Simulate a Lambda event with an authorized user."""
    return {
        "headers": {
            "origin": "testnet.marketplace.dev",
        },
        "requestContext": {
            "authorizer": {
                "claims": {
                    "cognito:username": "integrationuser",
                    "email": TEST_USER,
                    "sub": "acc-test-003",
                }
            }
        },
    }


@pytest.fixture
def lambda_event_authorized_not_found() -> dict:
    return {
        "headers": {
            "origin": "testnet.marketplace.dev",
        },
        "requestContext": {
            "authorizer": {
                "claims": {
                    "cognito:username": "integrationuser_not_found",
                    "email": "integrationuser_not_found@example.com",
                    "sub": "acc-test-003",
                }
            }
        },
    }


@pytest.fixture
def create_test_users(db_session: Session) -> Generator[List[User], None, None]:
    """Create multiple test users directly using session."""
    users = [
        User(
            row_id=1,
            account_id="acc-test-001",
            username="user1@example.com",
            name="Test User One",
            email="user1@example.com",
            email_verified=True,
            email_alerts=False,
            status=True,
            is_terms_accepted=True,
        ),
        User(
            row_id=2,
            account_id="acc-test-002",
            username="user2@example.com",
            name="Test User Two",
            email="user2@example.com",
            email_verified=True,
            email_alerts=False,
            status=True,
            is_terms_accepted=True,
        ),
        User(
            row_id=3,
            account_id="acc-test-003",
            username=TEST_USER,  # for handler test
            name="Integration User 1",
            email=TEST_USER,
            email_verified=True,
            email_alerts=False,
            status=True,
            is_terms_accepted=True,
        ),
    ]

    db_session.add_all(users)
    db_session.commit()

    yield users

    for user in users:
        db_session.delete(user)
    db_session.commit()


@pytest.fixture
def create_user_for_deleting(db_session: Session) -> Generator[User, None, None]:
    user = User(
        row_id=101,
        account_id="acc-test-004",
        username=TEST_USER,
        name="Integration User DELETE",
        email=TEST_USER,
        email_verified=True,
        email_alerts=False,
        status=True,
        is_terms_accepted=True,
    )

    db_session.add(user)
    db_session.commit()

    yield user


@pytest.fixture
def create_test_user_preferences(
    db_session: Session, create_test_users: List[User]
) -> Generator[List[UserPreferenceDomain], None, None]:
    """Create test user preferences directly."""
    user = create_test_users[2]  # integrationuser

    preferences_db = [
        UserPreference(
            user_row_id=user.row_id,
            preference_type="FEATURE_RELEASE",
            communication_type="EMAIL",
            source="MARKETPLACE_DAPP",
            opt_out_reason=None,
            status=True,
        ),
        UserPreference(
            user_row_id=user.row_id,
            preference_type="FEATURE_RELEASE",
            communication_type="SMS",
            source="MARKETPLACE_DAPP",
            opt_out_reason=None,
            status=True,
        ),
    ]

    db_session.add_all(preferences_db)
    db_session.commit()

    yield UserFactory.user_preferences_from_db_model(preferences_db)

    for pref in preferences_db:
        db_session.delete(pref)
    db_session.commit()


@pytest.fixture
def create_test_user_feedback_vote(
    db_session: Session, create_test_users: List[User]
) -> Generator[Tuple[UserServiceVoteDomain, UserServiceFeedbackDomain], None, None]:
    user = create_test_users[2]
    org_id = "test_org"
    service_id = "test_service"

    feedback = UserServiceFeedback(
        user_row_id=user.row_id, org_id=org_id, service_id=service_id, comment="test"
    )

    vote = UserServiceVote(
        user_row_id=user.row_id, org_id=org_id, service_id=service_id, rating=5.0
    )

    db_session.add_all([vote, feedback])
    db_session.commit()

    yield (
        UserFactory.user_service_vote_from_db_model(vote),
        UserFactory.user_service_feedback_from_db_model(feedback),
    )

    db_session.delete(vote)
    db_session.delete(feedback)
    db_session.commit()


@pytest.fixture
def post_confirmation_cognito_event() -> dict:
    return {
        "version": "1.0",
        "triggerSource": "PostConfirmation_ConfirmSignUp",
        "region": "us-east-1",
        "userPoolId": "us-east-1_example",
        "userName": "new_test_user",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "exampleClientId",
        },
        "request": {
            "userAttributes": {
                "sub": "12345678-1234-1234-1234-123456789012",
                "email_verified": "true",
                "email": "user@example.com",
                "cognito:username": "new_test_user",
            }
        },
        "response": {},
    }


@pytest.fixture
def fake_cognito_users() -> List[NewUser]:
    return [
        NewUser(
            account_id="abc123",
            username="testuser",
            name="Test User",
            email="test@example.com",
            email_verified=True,
            email_alerts=True,
            status=True,
            is_terms_accepted=True,
        )
    ]


@pytest.fixture
def mock_user_identity_manager(fake_cognito_users: List[NewUser]):
    class MockUserIdentityManager:
        def get_all_users(self) -> List[NewUser]:
            return fake_cognito_users

    return MockUserIdentityManager()
