import pytest
import os
from datetime import datetime, UTC, timedelta
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from deployer.config import NETWORKS, NETWORK_ID
from deployer.infrastructure.models import (
    Daemon, Order, EVMTransaction, ClaimingPeriod, 
    TransactionsMetadata, DaemonStatus, OrderStatus, 
    EVMTransactionStatus, ClaimingPeriodStatus
)
from deployer.domain.models.daemon import NewDaemonDomain
from deployer.domain.models.order import NewOrderDomain
from deployer.domain.models.evm_transaction import NewEVMTransactionDomain
from deployer.domain.models.claiming_period import NewClaimingPeriodDomain
from deployer.infrastructure.repositories.daemon_repository import DaemonRepository
from deployer.infrastructure.repositories.order_repository import OrderRepository
from deployer.infrastructure.repositories.transaction_repository import TransactionRepository
from deployer.infrastructure.repositories.claiming_period_repository import ClaimingPeriodRepository
from deployer.infrastructure.db import DefaultSessionFactory

# Test database configuration
db_config = NETWORKS[NETWORK_ID]['db']
TEST_DB_URL = (
    f"{db_config['DB_DRIVER']}://{db_config['DB_USER']}:{db_config['DB_PASSWORD']}"
    f"@{db_config['DB_HOST']}:{db_config['DB_PORT']}/{db_config['DB_NAME']}"
)

engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
TestSession = sessionmaker(bind=engine)


def cleanup_test_db():
    """Clear all tables in the test database."""
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        for table in tables:
            if table not in ['alembic_version']:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the database schema once per test session."""
    cleanup_test_db()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembic_cfg, "head")
    yield
    cleanup_test_db()


@pytest.fixture(scope="function", autouse=True)
def clean_data(setup_database):
    """Truncate data in all tables before each test, keeping schema."""
    yield
    # Clean up after each test
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        for table in tables:
            if table not in ['alembic_version']:
                conn.execute(text(f"TRUNCATE TABLE {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


@pytest.fixture(scope="function")
def db_session():
    """Provide a new database session for each test."""
    session = TestSession()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function", autouse=True)
def mock_session_factory(db_session):
    """Replace the default session factory with test session."""
    with patch('deployer.infrastructure.db.DefaultSessionFactory') as mock_factory:
        mock_factory.return_value = db_session
        with patch('deployer.application.services.daemon_service.DefaultSessionFactory', mock_factory):
            with patch('deployer.application.services.order_service.DefaultSessionFactory', mock_factory):
                with patch('deployer.application.services.transaction_service.DefaultSessionFactory', mock_factory):
                    with patch('deployer.application.services.job_services.DefaultSessionFactory', mock_factory):
                        with patch('deployer.application.services.authorization_service.DefaultSessionFactory', mock_factory):
                            yield db_session


# ========================= Test Data Factory =========================

class TestDataFactory:
    """Factory for creating test data domains."""
    
    @staticmethod
    def create_daemon_data(
        daemon_id: str = "test-daemon-123",
        account_id: str = "test-account-123",
        org_id: str = "test-org",
        service_id: str = "test-service",
        status: DaemonStatus = DaemonStatus.INIT,
        service_published: bool = True,
        **kwargs
    ) -> NewDaemonDomain:
        """Build daemon domain data."""
        current_time = datetime.now(UTC)
        defaults = {
            "daemon_config": {
                "payment_channel_storage_type": "etcd",
                "service_endpoint": "https://test-endpoint.com",
                "daemon_group": "default_group",
                "service_class": "test.ServiceClass"
            },
            "daemon_endpoint": "https://test-org-test-service.daemon.io",
            "start_at": current_time,
            "end_at": current_time + timedelta(days=30)
        }
        defaults.update(kwargs)
        
        return NewDaemonDomain(
            id=daemon_id,
            account_id=account_id,
            org_id=org_id,
            service_id=service_id,
            status=status,
            service_published=service_published,
            **defaults
        )
    
    @staticmethod
    def create_order_data(
        order_id: str = "test-order-123",
        daemon_id: str = "test-daemon-123",
        status: OrderStatus = OrderStatus.PROCESSING,
        **kwargs
    ) -> NewOrderDomain:
        """Build order domain data."""
        defaults = {}
        defaults.update(kwargs)
        
        return NewOrderDomain(
            id=order_id,
            daemon_id=daemon_id,
            status=status,
            **defaults
        )
    
    @staticmethod
    def create_transaction_data(
        hash: str = "0x123abc",
        order_id: str = "test-order-123",
        status: EVMTransactionStatus = EVMTransactionStatus.PENDING,
        **kwargs
    ) -> NewEVMTransactionDomain:
        """Build transaction domain data."""
        defaults = {
            "sender": "0xSenderAddress123",
            "recipient": "0xRecipientAddress456"
        }
        defaults.update(kwargs)
        
        return NewEVMTransactionDomain(
            hash=hash,
            order_id=order_id,
            status=status,
            **defaults
        )
    
    @staticmethod
    def create_claiming_period_data(
        daemon_id: str = "test-daemon-123",
        status: ClaimingPeriodStatus = ClaimingPeriodStatus.ACTIVE,
        **kwargs
    ) -> NewClaimingPeriodDomain:
        """Build claiming period domain data."""
        current_time = datetime.now(UTC)
        defaults = {
            "start_at": current_time,
            "end_at": current_time + timedelta(hours=1)
        }
        defaults.update(kwargs)
        
        return NewClaimingPeriodDomain(
            daemon_id=daemon_id,
            status=status,
            **defaults
        )
    
    @staticmethod
    def create_transactions_metadata(
        recipient: str = "0xRecipientAddress456",
        **kwargs
    ):
        """Create transactions metadata for testing."""
        defaults = {
            "last_block_no": 1000,
            "fetch_limit": 100,
            "block_adjustment": 5
        }
        defaults.update(kwargs)
        
        metadata = TransactionsMetadata(
            recipient=recipient,
            **defaults
        )
        return metadata


# ========================= Base Fixtures =========================

@pytest.fixture
def test_data_factory():
    """Provides the test data factory class."""
    return TestDataFactory


@pytest.fixture
def daemon_repo(db_session):
    """Provides the daemon repository."""
    return DaemonRepository


@pytest.fixture
def order_repo(db_session):
    """Provides the order repository."""
    return OrderRepository


@pytest.fixture
def transaction_repo(db_session):
    """Provides the transaction repository."""
    return TransactionRepository


@pytest.fixture
def claiming_period_repo(db_session):
    """Provides the claiming period repository."""
    return ClaimingPeriodRepository


# ========================= Mock External Services =========================

@pytest.fixture
def mock_haas_client():
    """Mock HaaS client for testing."""
    with patch('deployer.application.services.daemon_service.HaaSClient') as mock:
        client_instance = Mock()
        mock.return_value = client_instance
        
        # Default mock behaviors
        client_instance.start_daemon.return_value = None
        client_instance.delete_daemon.return_value = None
        client_instance.redeploy_daemon.return_value = None
        client_instance.check_daemon.return_value = ("DOWN", None)
        client_instance.get_public_key.return_value = "test-public-key-123"
        
        yield client_instance


@pytest.fixture
def mock_deployer_client():
    """Mock Deployer client for testing."""
    with patch('deployer.application.services.daemon_service.DeployerClient') as mock:
        with patch('deployer.application.services.job_services.DeployerClient') as mock2:
            client_instance = Mock()
            mock.return_value = client_instance
            mock2.return_value = client_instance
            
            # Default mock behaviors
            client_instance.start_daemon.return_value = None
            client_instance.stop_daemon.return_value = None
            client_instance.redeploy_daemon.return_value = None
            client_instance.update_daemon_status.return_value = None
            
            yield client_instance


@pytest.fixture
def mock_storage_provider():
    """Mock Storage provider for testing."""
    with patch('deployer.application.services.job_services.StorageProvider') as mock:
        provider_instance = Mock()
        mock.return_value = provider_instance
        
        # Default mock behaviors
        provider_instance.get.return_value = {
            "groups": [{
                "endpoints": ["https://test-endpoint.com"],
                "group_name": "default_group"
            }],
            "service_api_source": "ipfs://test-source"
        }
        
        yield provider_instance


# ========================= Core Entities Fixtures =========================

@pytest.fixture
def base_daemon(db_session, daemon_repo, test_data_factory):
    """Create a base daemon for tests."""
    daemon_data = test_data_factory.create_daemon_data()
    daemon_repo.create_daemon(db_session, daemon_data)
    db_session.commit()
    return daemon_data


@pytest.fixture
def base_order(db_session, order_repo, base_daemon, test_data_factory):
    """Create a base order for tests."""
    order_data = test_data_factory.create_order_data(daemon_id=base_daemon.id)
    order_repo.create_order(db_session, order_data)
    db_session.commit()
    return order_data


@pytest.fixture
def base_transaction(db_session, transaction_repo, base_order, test_data_factory):
    """Create a base transaction for tests."""
    transaction_data = test_data_factory.create_transaction_data(order_id=base_order.id)
    transaction_repo.upsert_transaction(db_session, transaction_data)
    db_session.commit()
    return transaction_data


@pytest.fixture
def base_claiming_period(db_session, base_daemon):
    """Create a base claiming period for tests."""
    current_time = datetime.now(UTC)
    claiming_period = ClaimingPeriod(
        daemon_id=base_daemon.id,
        start_at=current_time,
        end_at=current_time + timedelta(hours=1),
        status=ClaimingPeriodStatus.INACTIVE
    )
    db_session.add(claiming_period)
    db_session.commit()
    return claiming_period


# ========================= Lambda Event Helpers =========================

@pytest.fixture
def create_lambda_event():
    """Helper to create Lambda event structure."""
    def _create_event(
        path_params=None,
        query_params=None,
        body=None,
        headers=None,
        method="GET",
        path="/test"
    ):
        import json
        event = {
            "httpMethod": method,
            "path": path,
            "headers": headers or {
                "Authorization": "Bearer test-token",
                "x-cognito-username": "test-account-123"
            },
            "pathParameters": path_params or {},
            "queryStringParameters": query_params or {},
        }
        if body:
            event["body"] = json.dumps(body) if isinstance(body, dict) else body
        return event
    
    return _create_event