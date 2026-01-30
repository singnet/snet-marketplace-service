import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.mysql import MySqlContainer

from deployer.infrastructure.models import Base


@pytest.fixture(scope="session")
def test_container():
    with MySqlContainer("mysql:8", dialect="pymysql") as container:
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
    return sessionmaker(test_engine, expire_on_commit=False)
