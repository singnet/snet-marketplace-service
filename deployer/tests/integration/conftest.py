"""
Fixtures for deployer service integration tests.

Test Architecture:
==================
These are integration tests that verify the interaction between:
- Lambda handlers
- Application services
- Domain logic
- Database repositories
- Real MySQL database

What we mock (and why):
- External APIs (HaaS, blockchain) - cannot call in tests
- Logger - to reduce noise in test output

What we DON'T mock:
- Authorization logic - testing real access control
- Database - using real MySQL with test data
- Service layer - testing real business logic
- Repositories - testing real DB operations

This gives us confidence that our service works correctly
while keeping tests fast and deterministic.
"""

import io
import json
import pytest
from datetime import datetime, UTC, timedelta
from typing import Generator, Optional
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import close_all_sessions

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session as SessionType

from deployer.config import NETWORKS, NETWORK_ID
from deployer.infrastructure import db
from deployer.infrastructure.models import (
    DaemonStatus,
    OrderStatus,
    EVMTransactionStatus,
    ClaimingPeriodStatus,
)
from deployer.domain.models.daemon import NewDaemonDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.claiming_period import NewClaimingPeriodDomain
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository
from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository
from deployer.constant import DaemonStorageType
from deployer.utils import get_daemon_endpoint
from common.utils import generate_uuid


# Test database configuration
db_config = NETWORKS[NETWORK_ID]["db"]
TEST_DB_URL = (
    f"{db_config['DB_DRIVER']}://{db_config['DB_USER']}:{db_config['DB_PASSWORD']}"
    f"@{db_config['DB_HOST']}:{db_config['DB_PORT']}/{db_config['DB_NAME']}"
)

# Create test engine and session factory
test_engine = create_engine(TEST_DB_URL, pool_pre_ping=True, echo=False)
TestSessionFactory = sessionmaker(bind=test_engine)


@pytest.fixture(scope="function", autouse=True)
def mock_boto3_client():
    with patch("boto3.client") as mock_client_factory:
        mock = MagicMock()

        # DeployerClient expects response with 'body' field containing JSON
        def mock_invoke(*args, **kwargs):
            payload_data = json.dumps({"body": json.dumps({"status": "success", "data": {}})})
            payload_stream = io.BytesIO(payload_data.encode())
            return {
                "StatusCode": 200,
                "Payload": payload_stream,
            }
        
        mock.invoke = mock_invoke
        mock_client_factory.return_value = mock
        yield


def cleanup_test_db():
    """Clear all tables in the test database."""
    try:
        close_all_sessions()
    except Exception:
        pass
    with test_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        for table in tables:
            if table == "order":
                conn.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
            else:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the database schema once per test session."""
    cleanup_test_db()

    # Setup alembic config
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)

    # Run migrations
    command.upgrade(alembic_cfg, "head")

    yield

    # Cleanup after all tests
    cleanup_test_db()


@pytest.fixture(scope="function", autouse=True)
def clean_data(setup_database):
    """Truncate data in all tables before each test, keeping schema."""
    yield


    try:
        db_session.rollback()
        db_session.close()
    except Exception:
        pass

    try:
        close_all_sessions()
    except Exception:
        pass
    # Clean up after each test
    with test_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        for table in tables:
            if table not in ["alembic_version"]:
                if table == "order":
                    conn.execute(text(f"TRUNCATE TABLE `{table}`"))
                else:
                    conn.execute(text(f"TRUNCATE TABLE {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


@pytest.fixture(scope="function")
def db_session() -> Generator[SessionType, None, None]:
    """Provide a new database session for each test."""
    session = TestSessionFactory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function", autouse=True)
def mock_db_session_factory(db_session):
    """Replace the default session factory with test session factory."""
    original_factory = db.DefaultSessionFactory
    db.DefaultSessionFactory = TestSessionFactory
    yield
    db.DefaultSessionFactory = original_factory


@pytest.fixture(scope="function")
def mock_haas_client():
    """Mock HaaS client for daemon operations.

    NOTE: This is necessary for integration tests as we cannot call real HaaS API.
    This is acceptable as we're testing our service logic, not HaaS integration.
    """
    with patch("deployer.infrastructure.clients.haas_client.HaasClient") as mock_client:
        instance = MagicMock()
        mock_client.return_value = instance

        # Mock successful responses
        instance.create_daemon.return_value = {"status": "success", "daemon_id": "test-daemon-id"}
        instance.delete_daemon.return_value = {"status": "success"}
        instance.get_daemon_status.return_value = {"status": "running"}

        yield instance


@pytest.fixture(scope="function")
def mock_deployer_client():
    """Mock Deployer client for blockchain operations."""
    with patch("deployer.infrastructure.clients.deployer_cleint.DeployerClient") as mock_client:
        instance = MagicMock()
        mock_client.return_value = instance

        # Mock successful responses
        instance.get_service_info.return_value = {
            "service_endpoint": "https://test-service.example.com",
            "published": True,
        }
        instance.get_transaction_status.return_value = "success"

        yield instance


# ========================= Lambda Event Factories =========================


@pytest.fixture
def lambda_context():
    """Create a mock Lambda context."""
    context = MagicMock()
    context.function_name = "test-function"
    context.request_id = "test-request-id"
    context.invoked_function_arn = "arn:aws:lambda:region:account:function:test"
    context.memory_limit_in_mb = 128
    context.aws_request_id = "test-aws-request-id"
    return context


@pytest.fixture
def authorized_event():
    """Create a basic authorized Lambda event."""
    return {
        "headers": {
            "origin": "https://marketplace.singularitynet.io",
            "content-type": "application/json",
        },
        "requestContext": {
            "authorizer": {
                "claims": {
                    "cognito:username": "test-user",
                    "email": "test@example.com",
                    "sub": "test-user-id-123",
                }
            }
        },
        "httpMethod": "POST",
        "resource": "/order",
        "path": "/order",
    }


@pytest.fixture
def initiate_order_event(authorized_event):
    """Create an event for initiate_order handler."""
    authorized_event.update(
        {
            "body": '{"orgId": "test-org", "serviceId": "test-service"}',
            "httpMethod": "POST",
            "resource": "/order",
            "path": "/order",
        }
    )
    return authorized_event


@pytest.fixture
def initiate_order_event_with_credentials(authorized_event):
    """Create an event for initiate_order handler with service credentials."""
    authorized_event.update(
        {
            "body": '{"orgId": "test-org", "serviceId": "test-service", '
            '"serviceEndpoint": "https://custom-endpoint.com", '
            '"serviceCredentials": [{"key": "API_KEY", "value": "test-key", "isSecret": true}]}'
        }
    )
    return authorized_event


@pytest.fixture
def get_order_event(authorized_event):
    """Create an event for get_order handler."""
    authorized_event.update(
        {
            "pathParameters": {"orderId": "test-order-id"},
            "httpMethod": "GET",
            "resource": "/order/{orderId}",
            "path": "/order/test-order-id",
        }
    )
    return authorized_event


@pytest.fixture
def save_evm_transaction_event(authorized_event):
    """Create an event for save_evm_transaction handler."""
    authorized_event.update(
        {
            "body": json.dumps(
                {
                    "orderId": "test-order-id",
                    "transactionHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    "sender": "0xSenderAddress1234567890abcdef1234567890",
                    "recipient": "0xRecipientAddress1234567890abcdef123456",
                }
            ),
            "httpMethod": "POST",
            "resource": "/transaction",
            "path": "/transaction",
        }
    )
    return authorized_event


@pytest.fixture
def get_transactions_event(authorized_event):
    """Create an event for get_transactions handler."""
    authorized_event.update(
        {
            "queryStringParameters": {"orderId": "test-order-id"},
            "httpMethod": "GET",
            "resource": "/transactions",
            "path": "/transactions",
        }
    )
    return authorized_event


@pytest.fixture
def get_service_daemon_event(authorized_event):
    """Create an event for get_service_daemon handler."""
    authorized_event.update(
        {
            "pathParameters": {"daemonId": "test-daemon-id"},
            "httpMethod": "GET",
            "resource": "/daemon/{daemonId}",
            "path": "/daemon/test-daemon-id",
        }
    )
    return authorized_event


@pytest.fixture
def get_user_daemons_event(authorized_event):
    """Create an event for get_user_daemons handler."""
    authorized_event.update(
        {
            "httpMethod": "GET",
            "resource": "/daemons",
            "path": "/daemons",
        }
    )
    return authorized_event


@pytest.fixture
def start_daemon_for_claiming_event(authorized_event):
    """Create an event for start_daemon_for_claiming handler."""
    authorized_event.update(
        {
            "pathParameters": {"daemonId": "test-daemon-id"},
            "httpMethod": "GET",
            "resource": "/daemon/{daemonId}/start",
            "path": "/daemon/test-daemon-id/start",
        }
    )
    return authorized_event


@pytest.fixture
def pause_daemon_event(authorized_event):
    """Create an event for pause_daemon handler."""
    authorized_event.update(
        {
            "pathParameters": {"daemonId": "test-daemon-id"},
            "httpMethod": "GET",
            "resource": "/daemon/{daemonId}/pause",
            "path": "/daemon/test-daemon-id/pause",
        }
    )
    return authorized_event


@pytest.fixture
def unpause_daemon_event(authorized_event):
    """Create an event for unpause_daemon handler."""
    authorized_event.update(
        {
            "pathParameters": {"daemonId": "test-daemon-id"},
            "httpMethod": "GET",
            "resource": "/daemon/{daemonId}/unpause",
            "path": "/daemon/test-daemon-id/unpause",
        }
    )
    return authorized_event


@pytest.fixture
def update_config_event(authorized_event):
    """Create an event for update_config handler."""
    authorized_event.update(
        {
            "pathParameters": {"daemonId": "test-daemon-id"},
            "body": json.dumps({
                "serviceEndpoint": "https://new-endpoint.example.com",
                "serviceCredentials": [
                    {
                        "key": "API_KEY",
                        "value": "new-test-key",
                        "location": "header"
                    }
                ]
            }),
            "httpMethod": "POST",
            "resource": "/daemon/{daemonId}/config",
            "path": "/daemon/test-daemon-id/config",
        }
    )
    return authorized_event


@pytest.fixture
def search_daemon_event(authorized_event):
    """Create an event for search_daemon handler."""
    authorized_event.update(
        {
            "queryStringParameters": {"orgId": "test-org", "serviceId": "test-service"},
            "httpMethod": "GET",
            "resource": "/daemon/search",
            "path": "/daemon/search",
        }
    )
    return authorized_event


# ========================= Test Data Factories =========================


class TestDataFactory:
    """Factory for creating test data.

    IMPORTANT: The default account_id="test-user-id-123" matches the 'sub' claim
    in the authorized_event fixture. This ensures authorization checks pass.
    If you change one, you must change the other!
    """

    @staticmethod
    def create_daemon(
        daemon_id: Optional[str] = None,
        account_id: str = "test-user-id-123",  # Must match authorized_event['sub']
        org_id: str = "test-org",
        service_id: str = "test-service",
        status: DaemonStatus = DaemonStatus.INIT,
        **kwargs,
    ) -> NewDaemonDomain:
        """Create a daemon domain object."""
        if daemon_id is None:
            daemon_id = generate_uuid()

        current_time = datetime.now(UTC)
        defaults = {
            "daemon_config": {"payment_channel_storage_type": DaemonStorageType.ETCD.value},
            "service_published": False,
            "daemon_endpoint": get_daemon_endpoint(org_id, service_id),
            "start_at": current_time,
            "end_at": current_time + timedelta(days=30),
        }
        defaults.update(kwargs)

        return NewDaemonDomain(
            id=daemon_id,
            account_id=account_id,
            org_id=org_id,
            service_id=service_id,
            status=status,
            **defaults,
        )

    @staticmethod
    def create_order(
        order_id: Optional[str] = None,
        daemon_id: str = "test-daemon-id",
        status: OrderStatus = OrderStatus.PROCESSING,
    ) -> NewOrderDomain:
        """Create an order domain object."""
        if order_id is None:
            order_id = generate_uuid()

        return NewOrderDomain(id=order_id, daemon_id=daemon_id, status=status)

    @staticmethod
    def create_transaction(
        hash: Optional[str] = None,
        order_id: str = "test-order-id",
        status: EVMTransactionStatus = EVMTransactionStatus.PENDING,
        **kwargs,
    ) -> NewEVMTransactionDomain:
        """Create a transaction domain object."""
        if hash is None:
            hash = f"0x{''.join(['a' for _ in range(64)])}"

        defaults = {"sender": "0x1234567890abcdef", "recipient": "0xabcdef1234567890"}
        defaults.update(kwargs)

        return NewEVMTransactionDomain(hash=hash, order_id=order_id, status=status, **defaults)

    @staticmethod
    def create_claiming_period(
        daemon_id: str = "test-daemon-id",
        status: ClaimingPeriodStatus = ClaimingPeriodStatus.INACTIVE,
        **kwargs,
    ) -> NewClaimingPeriodDomain:
        """Create a claiming period domain object."""
        current_time = datetime.now(UTC)
        defaults = {"start_at": current_time, "end_at": current_time + timedelta(hours=24)}
        defaults.update(kwargs)

        return NewClaimingPeriodDomain(daemon_id=daemon_id, status=status, **defaults)


@pytest.fixture
def test_data_factory():
    """Provide the test data factory."""
    return TestDataFactory


# ========================= Database Fixtures =========================


@pytest.fixture
def daemon_repo():
    """Provide DaemonRepository class."""
    return DaemonRepository


@pytest.fixture
def order_repo():
    """Provide OrderRepository class."""
    return OrderRepository


@pytest.fixture
def transaction_repo():
    """Provide TransactionRepository class."""
    return TransactionRepository


@pytest.fixture
def claiming_period_repo():
    """Provide ClaimingPeriodRepository class."""
    return ClaimingPeriodRepository


@pytest.fixture
def test_daemon(db_session, daemon_repo, test_data_factory):
    """Create a test daemon in the database."""
    daemon = test_data_factory.create_daemon()
    daemon_repo.create_daemon(db_session, daemon)
    db_session.commit()
    return daemon


@pytest.fixture
def test_daemon_ready(db_session, daemon_repo, test_data_factory):
    """Create a test daemon with READY_TO_START status."""
    daemon = test_data_factory.create_daemon(status=DaemonStatus.READY_TO_START)
    daemon_repo.create_daemon(db_session, daemon)
    db_session.commit()
    return daemon


@pytest.fixture
def test_daemon_up(db_session, daemon_repo, test_data_factory):
    """Create a test daemon with UP status."""
    daemon = test_data_factory.create_daemon(status=DaemonStatus.UP)
    daemon_repo.create_daemon(db_session, daemon)
    db_session.commit()
    return daemon


@pytest.fixture
def test_daemon_down(db_session, daemon_repo, test_data_factory):
    """Create a test daemon with DOWN status."""
    daemon = test_data_factory.create_daemon(status=DaemonStatus.DOWN)
    daemon_repo.create_daemon(db_session, daemon)
    db_session.commit()
    return daemon


@pytest.fixture
def test_order(db_session, order_repo, test_daemon, test_data_factory):
    """Create a test order in the database."""
    order = test_data_factory.create_order(daemon_id=test_daemon.id)
    order_repo.create_order(db_session, order)
    db_session.commit()
    return order


@pytest.fixture
def test_transaction(db_session, transaction_repo, test_order, test_data_factory):
    """Create a test transaction in the database."""
    transaction = test_data_factory.create_transaction(order_id=test_order.id)
    transaction_repo.upsert_transaction(db_session, transaction)
    db_session.commit()
    return transaction


# ========================= Mock External Services =========================


@pytest.fixture
def mock_contract_api():
    """Mock contract API calls."""
    with patch("deployer.application.services.order_service.get_service_info") as mock_get_info:
        mock_get_info.return_value = {
            "service_endpoint": "https://test-service.example.com",
            "published": True,
            "groups": [{"group_id": "default-group"}],
        }
        yield mock_get_info


# REMOVED: Authorization service should NOT be mocked in integration tests
# We want to test real authorization logic
# @pytest.fixture
# def mock_authorization_service():
#     """Mock authorization service."""
#     with patch('deployer.application.services.authorization_service.AuthorizationService') as mock_auth:
#         instance = MagicMock()
#         mock_auth.return_value = instance
#         instance.check_access.return_value = True
#         yield instance


@pytest.fixture(autouse=True)
def mock_logger():
    """Mock logger to prevent log output during tests."""
    with patch("deployer.application.handlers.order_handlers.logger") as mock_log:
        yield mock_log
