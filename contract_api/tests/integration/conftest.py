import pytest
import os
from datetime import datetime, UTC
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from contract_api.infrastructure.repositories import base_repository
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.infrastructure.models import (
    Organization, Service, ServiceMetadata, ServiceGroup, 
    ServiceEndpoint, ServiceTags, ServiceMedia, OrgGroup
)
from contract_api.domain.models.organization import NewOrganizationDomain
from contract_api.domain.models.org_group import NewOrgGroupDomain
from contract_api.domain.models.service import NewServiceDomain
from contract_api.domain.models.service_metadata import NewServiceMetadataDomain
from contract_api.domain.models.service_group import NewServiceGroupDomain
from contract_api.domain.models.service_endpoint import NewServiceEndpointDomain
from contract_api.domain.models.service_tag import NewServiceTagDomain
from contract_api.domain.models.service_media import NewServiceMediaDomain
from contract_api.infrastructure.repositories.new_organization_repository import NewOrganizationRepository
from contract_api.infrastructure.repositories.new_service_repository import NewServiceRepository
from contract_api.domain.factory.service_factory import ServiceFactory


# Конфигурация тестовой БД
db_config = NETWORKS[NETWORK_ID]['db']
TEST_DB_URL = (
    f"{db_config['DB_DRIVER']}://{db_config['DB_USER']}:{db_config['DB_PASSWORD']}"
    f"@{db_config['DB_HOST']}:{db_config['DB_PORT']}/{db_config['DB_NAME']}"
)

engine = create_engine(TEST_DB_URL, pool_pre_ping=True)
TestSession = sessionmaker(bind=engine)


def cleanup_test_db():
    """Очистка тестовой базы данных."""
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()


@pytest.fixture(scope="function", autouse=True)
def reset_database():
    cleanup_test_db()

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembic_cfg, "head")
    

@pytest.fixture(scope="function")
def db_session():
    """Создание тестовой сессии для каждого теста."""
    session = TestSession()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function", autouse=True)
def mock_db_session(db_session):
    """Замена сессии в BaseRepository на тестовую."""
    original_session = base_repository.default_session
    base_repository.default_session = db_session
    yield db_session
    base_repository.default_session = original_session


# ========================= Фабрики для создания тестовых данных =========================

class TestDataFactory:
    """Фабрика для создания тестовых данных."""
    
    @staticmethod
    def create_organization_data(
        org_id: str = "test-org",
        organization_name: str = "Test Organization",
        is_curated: bool = True,
        **kwargs
    ) -> NewOrganizationDomain:
        """Создание данных организации."""
        defaults = {
            "owner_address": "0x1234567890abcdef",
            "org_metadata_uri": "ipfs://test-hash",
            "org_assets_url": {"hero_image": "https://example.com/hero.jpg"},
            "description": {"en": "Test organization description"},
            "assets_hash": {"hero_image": "test-hash"},
            "contacts": [
                {
                    "contact_type": "support",
                    "email": "support@test.com", 
                    "phone": "+1234567890"
                }
            ]
        }
        defaults.update(kwargs)
        
        return NewOrganizationDomain(
            org_id=org_id,
            organization_name=organization_name,
            is_curated=is_curated,
            **defaults
        )
    
    @staticmethod
    def create_org_group_data(
        org_id: str,
        group_id: str = "default-group",
        group_name: str = "Default Group",
        **kwargs
    ) -> NewOrgGroupDomain:
        """Создание данных группы организации."""
        defaults = {
            "payment": {
                "payment_address": "0xabcdef1234567890",
                "payment_expiration_threshold": 3600,
                "payment_channel_storage_type": "etcd"
            }
        }
        defaults.update(kwargs)
        
        return NewOrgGroupDomain(
            org_id=org_id,
            group_id=group_id,
            group_name=group_name,
            **defaults
        )
    
    @staticmethod
    def create_service_data(
        org_id: str,
        service_id: str = "test-service",
        is_curated: bool = True,
        **kwargs
    ) -> NewServiceDomain:
        """Создание данных сервиса."""
        defaults = {
            "hash_uri": "ipfs://test-service-hash"
        }
        defaults.update(kwargs)
        
        return NewServiceDomain(
            org_id=org_id,
            service_id=service_id,
            is_curated=is_curated,
            **defaults
        )
    
    @staticmethod
    def create_service_metadata_data(
        service_row_id: int,
        org_id: str,
        service_id: str,
        display_name: str = "Test Service",
        **kwargs
    ) -> NewServiceMetadataDomain:
        """Создание метаданных сервиса."""
        defaults = {
            "description": "Test service description",
            "short_description": "Short test description",
            "url": "https://test-service.com",
            "json": "{}",
            "model_hash": "ipfs://test-model-hash",
            "encoding": "proto",
            "type": "grpc",
            "mpe_address": "0x1234567890abcdef",
            "assets_url": {"hero_image": "https://example.com/service-hero.jpg"},
            "assets_hash": {"hero_image": "test-service-hash"},
            "contributors": [{"name": "Test Developer", "email": "dev@test.com"}]
        }
        defaults.update(kwargs)
        
        return NewServiceMetadataDomain(
            service_row_id=service_row_id,
            org_id=org_id,
            service_id=service_id,
            display_name=display_name,
            **defaults
        )
    
    @staticmethod
    def create_service_group_data(
        service_row_id: int,
        org_id: str, 
        service_id: str,
        group_id: str = "default-group",
        **kwargs
    ) -> NewServiceGroupDomain:
        """Создание группы сервиса."""
        defaults = {
            "group_name": "Default Group",
            "free_call_signer_address": "0xabcdef1234567890",
            "free_calls": 10,
            "pricing": [
                {
                    "default": True,
                    "price_model": "fixed_price",
                    "price_in_cogs": 1000
                }
            ]
        }
        defaults.update(kwargs)
        
        return NewServiceGroupDomain(
            service_row_id=service_row_id,
            org_id=org_id,
            service_id=service_id,
            group_id=group_id,
            **defaults
        )
    
    @staticmethod
    def create_service_endpoint_data(
        service_row_id: int,
        org_id: str,
        service_id: str, 
        group_id: str = "default-group",
        **kwargs
    ) -> NewServiceEndpointDomain:
        """Создание эндпоинта сервиса."""
        defaults = {
            "endpoint": "https://test-service-endpoint.com:8080",
            "is_available": True,
            "last_check_timestamp": datetime.now(UTC)
        }
        defaults.update(kwargs)
        
        return NewServiceEndpointDomain(
            service_row_id=service_row_id,
            org_id=org_id,
            service_id=service_id,
            group_id=group_id,
            **defaults
        )
    
    @staticmethod
    def create_service_tag_data(
        service_row_id: int,
        org_id: str,
        service_id: str,
        tag_name: str = "ai"
    ) -> NewServiceTagDomain:
        """Создание тега сервиса."""
        return NewServiceTagDomain(
            service_row_id=service_row_id,
            org_id=org_id,
            service_id=service_id,
            tag_name=tag_name
        )
    
    @staticmethod  
    def create_service_media_data(
        service_row_id: int,
        org_id: str,
        service_id: str,
        asset_type: str = "hero_image",
        **kwargs
    ) -> NewServiceMediaDomain:
        """Создание медиа сервиса."""
        defaults = {
            "url": "https://example.com/test-image.jpg",
            "order": 1,
            "file_type": "image",
            "alt_text": "Test image",
            "hash_uri": "ipfs://test-media-hash"
        }
        defaults.update(kwargs)
        
        return NewServiceMediaDomain(
            service_row_id=service_row_id,
            org_id=org_id,
            service_id=service_id,
            asset_type=asset_type,
            **defaults
        )


# ========================= Базовые фикстуры =========================

@pytest.fixture
def test_data_factory():
    """Предоставляет фабрику тестовых данных."""
    return TestDataFactory


@pytest.fixture
def org_repo(db_session):
    """Репозиторий организаций."""
    return NewOrganizationRepository()


@pytest.fixture  
def service_repo(db_session):
    """Репозиторий сервисов."""
    return NewServiceRepository()


# ========================= Базовые сущности =========================

@pytest.fixture
def base_organization(db_session, org_repo, test_data_factory):
    """Создает базовую организацию."""
    org_data = test_data_factory.create_organization_data()
    org_repo.upsert_organization(db_session, org_data)
    db_session.commit()  # Сначала сохраняем организацию
    
    # Теперь создаем группу для организации
    group_data = test_data_factory.create_org_group_data(org_data.org_id)
    org_repo.create_org_groups(db_session, [group_data])
    db_session.commit()  # И сохраняем группу
    
    return org_data


@pytest.fixture
def base_service(db_session, service_repo, base_organization, test_data_factory):
    """Создает базовый сервис с метаданными."""
    # Создаем сервис
    service_data = test_data_factory.create_service_data(base_organization.org_id)
    service = service_repo.upsert_service(db_session, service_data)
    
    # Создаем метаданные
    metadata_data = test_data_factory.create_service_metadata_data(
        service.row_id, base_organization.org_id, service_data.service_id
    )
    service_repo.upsert_service_metadata(db_session, metadata_data)
    
    # Создаем группу сервиса
    group_data = test_data_factory.create_service_group_data(
        service.row_id, base_organization.org_id, service_data.service_id
    )
    service_repo.upsert_service_group(db_session, group_data)
    
    # Создаем эндпоинт
    endpoint_data = test_data_factory.create_service_endpoint_data(
        service.row_id, base_organization.org_id, service_data.service_id
    )
    service_repo.upsert_service_endpoint(db_session, endpoint_data)
    
    db_session.commit()
    return service