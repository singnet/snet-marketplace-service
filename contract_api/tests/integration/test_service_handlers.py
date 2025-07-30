import pytest
import json
from sqlalchemy import select
from contract_api.infrastructure.models import Organization
from contract_api.application.services.service_service import ServiceService
from contract_api.infrastructure.models import Service, ServiceMetadata
from contract_api.application.schemas.service_schemas import GetServiceRequest
from contract_api.infrastructure.repositories.service_repository import ServiceRepository
from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository
from contract_api.application.handlers.service_handlers import *

def test_organization_inserted(test_organization, db_session):
    """
    Проверяем, что фикстура test_org добавила запись в таблицу organization.
    """
    # Ищем по org_id, который вернула фикстура test_org
    stmt = select(Organization).where(Organization.org_id == test_organization.org_id)
    result = db_session.execute(stmt).scalar_one_or_none()

    # Должна быть найдена ровно одна запись
    assert result is not None, "Organization was not inserted into the database"
    assert result.org_id == test_organization.org_id

# def test_service_inserted(test_organization, test_service, db_session):
#     request = GetServiceRequest.validate_event(event)
#     response = ServiceService().get_service(request)

def test_service_inserted(test_service, db_session):
    """
    Проверяем, что фикстура test_service добавила запись в таблицы:
      - service
      - service_metadata
    """
    # domain-объект, который вернула фикстура
    svc_domain = test_service

    # 1) Проверяем таблицу service
    stmt_svc = select(Service).where(
        Service.org_id   == svc_domain.org_id,
        Service.service_id == svc_domain.service_id
    )
    svc_row = db_session.execute(stmt_svc).scalar_one_or_none()
    assert svc_row is not None, "Запись в таблице service не найдена"
    assert svc_row.service_id == svc_domain.service_id
    assert svc_row.org_id     == svc_domain.org_id

    # 2) Проверяем таблицу service_metadata
    stmt_meta = select(ServiceMetadata).where(
        ServiceMetadata.service_row_id == svc_row.row_id
    )
    meta_row = db_session.execute(stmt_meta).scalar_one_or_none()
    assert meta_row is not None, "Запись в таблице service_metadata не найдена"
    assert meta_row.org_id     == svc_domain.org_id
    assert meta_row.service_id == svc_domain.service_id

def test_get_service(test_service, db_session):
    svc = test_service

    # Берём доменные объекты напрямую из репозитория
    service_dom, org_dom, meta_dom = ServiceRepository().get_service(svc.org_id, svc.service_id)

    # Получаем словари «short response»
    svc_keys = set(service_dom.to_short_response().keys())
    org_keys = set(org_dom.to_short_response().keys())
    meta_keys = set(meta_dom .to_short_response().keys())

    # Поля, которые дополняет ServiceService
    extra_keys = {"media", "tags", "isAvailable", "groups", "demoComponentRequired"}

    expected = svc_keys | org_keys | meta_keys | extra_keys

    # Выполняем сам вызов
    event    = {"pathParameters": {"orgId": svc.org_id, "serviceId": svc.service_id}}
    response = get_service(event = event,context = None)
    print(response)
    
    assert response["statusCode"] == 200

    data = json.loads(response["body"])["data"]
    print(data)

    assert set(data.keys()) == expected

def test_get_services_success(test_service, db_session):
    event = {}