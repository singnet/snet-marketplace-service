import os
from typing import Generator, List

import pytest
from dapp_user.domain.factory.user_factory import UserFactory
from dapp_user.domain.models.user import NewUser
from dapp_user.domain.models.user_preference import UserPreference as UserPreferenceDomain
from dapp_user.infrastructure.models import User, UserPreference
from dapp_user.infrastructure.repositories import base_repository
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from dapp_user.settings import settings
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config

TEST_DB_URL = (
    f"{settings.db.driver}://{settings.db.user}:{settings.db.password}"
    f"@{settings.db.host}:{settings.db.port}/{settings.db.name}"
)

engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
TestSession = sessionmaker(bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Provide the SQLAlchemy engine for the test DB."""
    return engine


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ALEMBIC_INI_PATH = os.path.join(ROOT_DIR, "alembic.ini")
TEST_USER = "integration@example.com"


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply Alembic migrations at the start of the test session."""
    alembic_cfg = Config(ALEMBIC_INI_PATH)
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="function")
def db_session(db_engine: Engine, apply_migrations) -> Generator[SessionType, None, None]:
    """Create a new database session for a test, rolling back after."""
    connection = db_engine.connect()
    session = TestSession(bind=connection)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        connection.close()


@pytest.fixture(scope="function", autouse=True)
def test_session(db_session: SessionType) -> Generator[SessionType, None, None]:
    """Monkeypatch BaseRepository to use test session."""
    original_session = base_repository.default_session
    base_repository.default_session = db_session
    try:
        yield db_session
    finally:
        base_repository.default_session = original_session


@pytest.fixture
def user_repo() -> UserRepository:
    """Return a real UserRepository that uses the overridden session."""
    return UserRepository()


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
def create_test_users(user_repo: UserRepository) -> Generator[List[User], None, None]:
    """Create multiple users in the real DB for testing."""
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

    user_repo.add_all_items(users)

    yield users

    for user in users:
        user_repo.session.delete(user)
    user_repo.session.commit()


@pytest.fixture
def create_user_for_deleting(user_repo: UserRepository) -> Generator[User, None, None]:
    user = User(
        row_id=3,
        account_id="acc-test-003",
        username=TEST_USER,  # for handler test
        name="Integration User DELETE",
        email=TEST_USER,
        email_verified=True,
        email_alerts=False,
        status=True,
        is_terms_accepted=True,
    )

    user_repo.add_item(user)

    yield user


@pytest.fixture
def create_test_user_preferences(
    user_repo: UserRepository, create_test_users: List[User]
) -> Generator[List[UserPreferenceDomain], None, None]:
    """Create test user preferences for a given user."""
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

    user_repo.add_all_items(preferences_db)
    user_repo.session.commit()

    yield UserFactory.user_preferences_from_db_model(preferences_db)

    for pref in preferences_db:
        user_repo.session.delete(pref)
    user_repo.session.commit()


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
def fake_cognito_users():
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
        def get_all_users(self):
            return fake_cognito_users

    return MockUserIdentityManager()
