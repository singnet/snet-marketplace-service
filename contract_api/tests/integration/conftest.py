import pytest
import os
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contract_api.infrastructure.repositories import base_repository
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.infrastructure.models import Service
from contract_api.infrastructure.repositories.service_repository import ServiceRepository
from contract_api.domain.models.organization import NewOrganizationDomain
from contract_api.infrastructure.repositories.new_organization_repository import NewOrganizationRepository
from contract_api.domain.models.service import NewServiceDomain
from contract_api.domain.models.service_metadata import NewServiceMetadataDomain
from contract_api.infrastructure.repositories.new_service_repository import NewServiceRepository
from contract_api.domain.factory.service_factory import ServiceFactory

# Build URL from config (like in db.py)
db_config = NETWORKS[NETWORK_ID]['db']
TEST_DB_URL = (
    f"{db_config['DB_DRIVER']}://{db_config['DB_USER']}:{db_config['DB_PASSWORD']}"
    f"@{db_config['DB_HOST']}:{db_config['DB_PORT']}/{db_config['DB_NAME']}"
)

engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
TestSession = sessionmaker(bind=engine)

def cleanup_test_db():
    """Clean up the test database."""
    with engine.connect() as conn:
        # Disable foreign key checks
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # Get all tables and drop them
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        # Re-enable foreign key checks
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply alembic migrations for tests."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembic_cfg, "head")
    yield
    # Instead of downgrade, just clean up the database
    cleanup_test_db()

@pytest.fixture(scope="function")
def db_session():
    """Create a test session for each test."""
    session = TestSession()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function", autouse=True)
def mock_db_session(db_session):
    """Replace the session in BaseRepository."""
    original_session = base_repository.default_session
    base_repository.default_session = db_session
    yield db_session
    base_repository.default_session = original_session

@pytest.fixture(scope="function")
def test_organization(
    db_session
):
    org_repo = NewOrganizationRepository()
    org_domain = NewOrganizationDomain(
        org_id = "test-org",
        organization_name="Test Org",
        owner_address="0x",
        org_metadata_uri="",
        org_assets_url={"hero_image":""},
        is_curated=True,
        description={},
        assets_hash={},
        contacts={}
    )  
    org_repo.upsert_organization(db_session, org_domain)
    db_session.commit()
    return org_domain

@pytest.fixture(scope="function")
def test_service(
        db_session, test_organization
):
    service_repo = NewServiceRepository()
    service_domain = NewServiceDomain(
        org_id = test_organization.org_id,
        service_id = "test-service-1",
        hash_uri = "",
        is_curated = True
    )

    service = service_repo.upsert_service(db_session, service_domain)

    metadata_dict = {}
    service_metadata_domain = ServiceFactory.service_metadata_from_metadata_dict(
        metadata_dict,
        service_row_id = service.row_id,
        org_id = test_organization.org_id,
        service_id = service.service_id,
    )
    service_repo.upsert_service_metadata(db_session, service_metadata_domain)

    db_session.commit()
    return service
