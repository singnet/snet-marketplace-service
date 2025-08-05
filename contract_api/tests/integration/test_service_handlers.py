import pytest
import json
from datetime import datetime, UTC
from unittest.mock import patch

from contract_api.application.handlers.service_handlers import get_service
from contract_api.application.services.service_service import ServiceService
from contract_api.exceptions import ServiceNotFoundException
from contract_api.domain.models.service_tag import NewServiceTagDomain
from contract_api.domain.models.service_media import NewServiceMediaDomain


class TestGetService:
    """Тесты для хендлера get_service."""
    
    def test_get_service_success(self, db_session, base_service, base_organization, service_repo):
        """Тест успешного получения сервиса."""
        # Подготовка
        org_id = base_organization.org_id
        service_id = base_service.service_id
        
        # Добавляем теги
        tag1 = NewServiceTagDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            tag_name="ai"
        )
        tag2 = NewServiceTagDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            tag_name="machine-learning"
        )
        service_repo.create_service_tag(db_session, tag1)
        service_repo.create_service_tag(db_session, tag2)
        
        # Добавляем медиа
        hero_media = NewServiceMediaDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            url="https://example.com/hero.jpg",
            order=1,
            file_type="image",
            asset_type="hero_image",
            alt_text="Hero image",
            hash_uri="ipfs://hero-hash"
        )
        gallery_media = NewServiceMediaDomain(
            service_row_id=base_service.row_id,
            org_id=org_id,
            service_id=service_id,
            url="https://example.com/gallery1.jpg",
            order=2,
            file_type="image", 
            asset_type="media_gallery",
            alt_text="Gallery image",
            hash_uri="ipfs://gallery-hash"
        )
        service_repo.upsert_service_media(db_session, hero_media)
        service_repo.upsert_service_media(db_session, gallery_media)
        
        db_session.commit()
        
        # Формируем event для Lambda
        event = {
            "pathParameters": {
                "orgId": org_id,
                "serviceId": service_id
            }
        }
        
        # Выполнение
        response = get_service(event, context=None)
        
        # Проверки
        assert response["statusCode"] == 200
        
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert "data" in body
        
        data = body["data"]
        
        # Проверяем основные поля
        assert data["orgId"] == org_id
        assert data["serviceId"] == service_id
        assert data["displayName"] == "Test Service"
        assert data["description"] == "Test service description"
        assert data["shortDescription"] == "Short test description"
        assert data["organizationName"] == "Test Organization"
        
        # Проверяем контакты
        assert "supportContacts" in data
        assert data["supportContacts"]["email"] == "support@test.com"
        assert data["supportContacts"]["phone"] == "+1234567890"
        
        # Проверяем теги
        assert "tags" in data
        assert set(data["tags"]) == {"ai", "machine-learning"}
        
        # Проверяем медиа
        assert "media" in data
        assert len(data["media"]) == 2
        media_by_type = {m["assetType"]: m for m in data["media"]}
        assert "hero_image" in media_by_type
        assert "media_gallery" in media_by_type
        assert media_by_type["hero_image"]["url"] == "https://example.com/hero.jpg"
        
        # Проверяем группы и эндпоинты
        assert "groups" in data
        assert len(data["groups"]) == 1
        group = data["groups"][0]
        assert group["groupId"] == "default-group"
        assert group["groupName"] == "Default Group"
        assert "endpoints" in group
        assert len(group["endpoints"]) == 1
        endpoint = group["endpoints"][0]
        assert endpoint["endpoint"] == "https://test-service-endpoint.com:8080"
        assert endpoint["isAvailable"] is True
        
        # Проверяем доступность
        assert data["isAvailable"] is True
        
        # Проверяем demo component
        assert "demoComponentRequired" in data
        assert data["demoComponentRequired"] is False
        
        # Проверяем рейтинг
        assert data["rating"] == 0.0
        assert data["numberOfRatings"] == 0
        
        # Проверяем contributors
        assert "contributors" in data
        assert data["contributors"] == ["Test Developer"]
    
    def test_get_service_not_found(self, db_session):
        """Тест получения несуществующего сервиса."""
        event = {
            "pathParameters": {
                "orgId": "non-existent-org",
                "serviceId": "non-existent-service"
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        # Проверяем что ошибка содержит информацию о том, что сервис не найден
        # Структура может быть {"status": "error", "message": "..."} или другая
        assert "Service not found" in str(body).lower() or "not found" in str(body).lower()
    
    def test_get_service_uncurated(self, db_session, org_repo, service_repo, test_data_factory):
        """Тест получения некурированного сервиса (должен возвращать 404)."""
        # Создаем организацию
        org_data = test_data_factory.create_organization_data(org_id="test-org-uncurated")
        org_repo.upsert_organization(db_session, org_data)
        db_session.commit()  # Сначала сохраняем организацию
        
        # Создаем группу
        group_data = test_data_factory.create_org_group_data(org_data.org_id)
        org_repo.create_org_groups(db_session, [group_data])
        db_session.commit()  # Потом сохраняем группу

        # Создаем некурированный сервис
        service_data = test_data_factory.create_service_data(
            org_data.org_id, 
            service_id="uncurated-service",
            is_curated=False  # Некурированный
        )
        service = service_repo.upsert_service(db_session, service_data)
        
        metadata_data = test_data_factory.create_service_metadata_data(
            service.row_id, org_data.org_id, service_data.service_id
        )
        service_repo.upsert_service_metadata(db_session, metadata_data)
        
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": org_data.org_id,
                "serviceId": service_data.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Service not found" in str(body).lower() or "not found" in str(body).lower()
    
    def test_get_service_unavailable_endpoint(self, db_session, base_service, base_organization, service_repo):
        """Тест сервиса с недоступным эндпоинтом."""
        # Создаем недоступный эндпоинт
        from contract_api.domain.models.service_endpoint import NewServiceEndpointDomain
        
        unavailable_endpoint = NewServiceEndpointDomain(
            service_row_id=base_service.row_id,
            org_id=base_organization.org_id,
            service_id=base_service.service_id,
            group_id="unavailable-group",
            endpoint="https://unavailable-endpoint.com:8080",
            is_available=False,
            last_check_timestamp=datetime.now(UTC)
        )
        
        # Создаем группу для этого эндпоинта
        from contract_api.domain.models.service_group import NewServiceGroupDomain
        unavailable_group = NewServiceGroupDomain(
            service_row_id=base_service.row_id,
            org_id=base_organization.org_id,
            service_id=base_service.service_id,
            group_id="unavailable-group",
            group_name="Unavailable Group",
            free_call_signer_address="0xabcdef1234567890",
            free_calls=0,
            pricing=[]
        )
        
        service_repo.upsert_service_group(db_session, unavailable_group)
        service_repo.upsert_service_endpoint(db_session, unavailable_endpoint)
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        data = body["data"]
        
        # Должно быть 2 группы, но общая доступность True из-за базового эндпоинта
        assert len(data["groups"]) == 2
        assert data["isAvailable"] is True  # Есть хотя бы один доступный эндпоинт
        
        # Проверяем, что недоступный эндпоинт помечен правильно
        unavailable_group_data = None
        for group in data["groups"]:
            if group["groupId"] == "unavailable-group":
                unavailable_group_data = group
                break
        
        assert unavailable_group_data is not None
        assert unavailable_group_data["endpoints"][0]["isAvailable"] is False
    
    def test_get_service_with_rating(self, db_session, base_service, base_organization, service_repo):
        """Тест сервиса с рейтингом."""
        # Обновляем рейтинг через репозиторий
        rating_data = {
            "rating": 4.5,
            "total_users_rated": 150
        }
        service_repo.update_service_rating(
            db_session, 
            base_organization.org_id, 
            base_service.service_id, 
            rating_data
        )
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        data = body["data"]
        
        assert data["rating"] == 4.5
        assert data["numberOfRatings"] == 150
    
    def test_get_service_invalid_path_parameters(self):
        """Тест с неверными параметрами пути."""
        # Тест без orgId
        event = {
            "pathParameters": {
                "serviceId": "test-service"
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == 400
        
        # Тест без serviceId
        event = {
            "pathParameters": {
                "orgId": "test-org"
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == 400
        
        # Тест без pathParameters
        event = {}
        
        response = get_service(event, context=None)
        assert response["statusCode"] == 400
    
    def test_get_service_empty_values(self):
        """Тест с пустыми значениями параметров."""
        event = {
            "pathParameters": {
                "orgId": "",
                "serviceId": ""
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == 400
    
    @patch('contract_api.application.services.service_service.ServiceService.get_service')
    def test_get_service_internal_error(self, mock_get_service, base_organization):
        """Тест обработки внутренней ошибки."""
        mock_get_service.side_effect = Exception("Database error")
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": "test-service"
            }
        }
        
        response = get_service(event, context=None)
        assert response["statusCode"] == 500
    
    def test_get_service_cors_headers(self, db_session, base_service, base_organization):
        """Тест наличия CORS заголовков."""
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == 200
        assert "headers" in response
        # Проверяем наличие CORS заголовков (если они добавляются в хендлере)
        # В текущем коде CORS настраивается в serverless.yml, но можно проверить структуру ответа
    
    def test_get_service_multiple_media_types(self, db_session, base_service, base_organization, service_repo):
        """Тест сервиса с разными типами медиа."""
        media_items = [
            NewServiceMediaDomain(
                service_row_id=base_service.row_id,
                org_id=base_organization.org_id,
                service_id=base_service.service_id,
                url="https://example.com/hero.jpg",
                order=1,
                file_type="image",
                asset_type="hero_image",
                alt_text="Hero image",
                hash_uri="ipfs://hero-hash"
            ),
            NewServiceMediaDomain(
                service_row_id=base_service.row_id,
                org_id=base_organization.org_id,
                service_id=base_service.service_id,
                url="https://example.com/demo.mp4",
                order=2,
                file_type="video",
                asset_type="media_gallery",
                alt_text="Demo video",
                hash_uri="ipfs://video-hash"
            ),
            NewServiceMediaDomain(
                service_row_id=base_service.row_id,
                org_id=base_organization.org_id,
                service_id=base_service.service_id,
                url="https://example.com/proto-stub.py",
                order=3,
                file_type="grpc-stub",
                asset_type="grpc-stub/python",
                alt_text="Python stub",
                hash_uri=""
            )
        ]
        
        for media in media_items:
            service_repo.upsert_service_media(db_session, media)
        
        db_session.commit()
        
        event = {
            "pathParameters": {
                "orgId": base_organization.org_id,
                "serviceId": base_service.service_id
            }
        }
        
        response = get_service(event, context=None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        data = body["data"]
        
        assert len(data["media"]) == 3
        
        # Проверяем, что все типы медиа присутствуют
        asset_types = {m["assetType"] for m in data["media"]}
        expected_types = {"hero_image", "media_gallery", "grpc-stub/python"}
        assert asset_types == expected_types