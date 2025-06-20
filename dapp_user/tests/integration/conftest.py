from typing import Generator, List

import pytest
from dapp_user.infrastructure.models import User
from dapp_user.infrastructure.repositories import base_repository
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from dapp_user.settings import settings
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker

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


@pytest.fixture(scope="function")
def db_session(db_engine: Engine) -> Generator[SessionType, None, None]:
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
        "requestContext": {
            "authorizer": {
                "claims": {
                    "cognito:username": "integrationuser",
                    "email": "integrationuser",
                }
            }
        }
    }


@pytest.fixture
def create_test_users(user_repo: UserRepository) -> Generator[List[User], None, None]:
    """Create multiple users in the real DB for testing."""
    users = [
        User(
            row_id=1,
            account_id="acc-test-001",
            username="user1",
            name="Test User One",
            email="user1@example.com",
            email_verified=b"1",
            email_alerts=b"0",
            status=b"1",
            request_id="req-001",
            request_time_epoch="1700000000",
            is_terms_accepted=b"1",
        ),
        User(
            row_id=2,
            account_id="acc-test-002",
            username="user2",
            name="Test User Two",
            email="user2@example.com",
            email_verified=b"1",
            email_alerts=b"0",
            status=b"1",
            request_id="req-001",
            request_time_epoch="1700000000",
            is_terms_accepted=b"1",
        ),
        User(
            row_id=3,
            account_id="acc-test-003",
            username="integrationuser",  # for handler test
            name="Integration User",
            email="integration@example.com",
            email_verified=b"1",
            email_alerts=b"0",
            status=b"1",
            request_id="req-001",
            request_time_epoch="1700000000",
            is_terms_accepted=b"1",
        ),
    ]

    user_repo.add_all_items(users)

    yield users

    for user in users:
        user_repo.session.delete(user)
    user_repo.session.commit()
