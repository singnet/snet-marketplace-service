import os

import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from testcontainers.mysql import MySqlContainer

from deployer.domain.schemas.haas_responses import GetCallEventsResponse
from deployer.infrastructure.db import session_scope
from deployer.infrastructure.models import Base

os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"


@pytest.fixture(scope="session")
def test_container():
    with MySqlContainer("mysql:8.0", dialect="pymysql") as container:
        yield container


@pytest.fixture(scope="session")
def test_engine(test_container):
    engine = create_engine(test_container.get_connection_url(), echo=False)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session_factory(test_engine):
    session_factory = sessionmaker(test_engine, expire_on_commit=False)

    yield session_factory

    with session_scope(session_factory) as session:
        metadata = Base.metadata
        for table in reversed(metadata.sorted_tables):
            session.execute(delete(table))


@pytest.fixture(scope="function")
def db_session(test_session_factory):
    with session_scope(test_session_factory) as session:
        yield session


@pytest.fixture(scope="function")
def test_account_id():
    return "SERVERLESS_OFFLINE_ACCOUNT_ID"


@pytest.fixture(scope="function")
def test_org_id():
    return "TEST_ORG_ID"


@pytest.fixture(scope="function")
def test_service_id():
    return "TEST_SERVICE_ID"


@pytest.fixture(scope="function")
def test_daemon_id():
    return "TEST_DAEMON_ID"


@pytest.fixture(scope="function")
def test_hosted_service_id():
    return "TEST_HOSTED_SERVICE_ID"


@pytest.fixture(scope="function")
def test_haas_client():
    class TestHaaSClient:
        def __init__(self):
            self.daemon_logs = ["log1", "log2", "log3"]
            self.service_logs = []
            self.public_key = "PUBLIC_KEY"
            self.call_events = GetCallEventsResponse(events=[], totalCount=0)

        def deploy_daemon(self, *args, **kwargs):
            return None

        def delete_daemon(self, *args, **kwargs):
            return None

        def get_daemon_logs(self, *args, **kwargs):
            return self.daemon_logs

        def get_public_key(self, *args, **kwargs):
            return self.public_key

        def delete_hosted_service(self, *args, **kwargs):
            return None

        def get_hosted_service_logs(self, *args, **kwargs):
            return self.service_logs

        def get_call_events(self, *args, **kwargs):
            return self.call_events

    return TestHaaSClient()


@pytest.fixture(scope="function")
def test_deployer_client():
    class TestDeployerClient:
        def deploy_daemon(self, *args, **kwargs):
            return None

    return TestDeployerClient()


@pytest.fixture(scope="function")
def test_registry_client(test_org_id):
    class TestRegistryClient:
        def get_all_orgs(self, *args, **kwargs):
            return [{"org_id": test_org_id}]

    return TestRegistryClient()


@pytest.fixture(scope="function")
def test_crypto_exchange_client():
    class TestCryptoExchangeClient:
        def __init__(self):
            self.token_rate = 0.5

        def get_token_rate(self, *args, **kwargs) -> float:
            return self.token_rate

    return TestCryptoExchangeClient()
