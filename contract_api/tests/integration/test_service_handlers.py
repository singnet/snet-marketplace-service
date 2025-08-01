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
    Check that the test_organization fixture added a record to the organization table.
    """
    # Search by org_id returned by the test_organization fixture
    stmt = select(Organization).where(Organization.org_id == test_organization.org_id)
    result = db_session.execute(stmt).scalar_one_or_none()

    # Exactly one record should be found
    assert result is not None, "Organization was not inserted into the database"
    assert result.org_id == test_organization.org_id

# def test_service_inserted(test_organization, test_service, db_session):
#     request = GetServiceRequest.validate_event(event)
#     response = ServiceService().get_service(request)

def test_service_inserted(test_service, db_session):
    """
    Check that the test_service fixture added records to the tables:
      - service
      - service_metadata
    """
    # Domain object returned by the fixture
    svc_domain = test_service

    # 1) Check the service table
    stmt_svc = select(Service).where(
        Service.org_id   == svc_domain.org_id,
        Service.service_id == svc_domain.service_id
    )
    svc_row = db_session.execute(stmt_svc).scalar_one_or_none()
    assert svc_row is not None, "Record not found in service table"
    assert svc_row.service_id == svc_domain.service_id
    assert svc_row.org_id     == svc_domain.org_id

    # 2) Check the service_metadata table
    stmt_meta = select(ServiceMetadata).where(
        ServiceMetadata.service_row_id == svc_row.row_id
    )
    meta_row = db_session.execute(stmt_meta).scalar_one_or_none()
    assert meta_row is not None, "Record not found in service_metadata table"
    assert meta_row.org_id     == svc_domain.org_id
    assert meta_row.service_id == svc_domain.service_id

def test_get_service(test_service, db_session):
    svc = test_service

    # Get domain objects directly from the repository
    service_dom, org_dom, meta_dom = ServiceRepository().get_service(svc.org_id, svc.service_id)

    # Get "short response" dictionaries
    svc_keys = set(service_dom.to_short_response().keys())
    org_keys = set(org_dom.to_short_response().keys())
    meta_keys = set(meta_dom .to_short_response().keys())

    # Fields that ServiceService adds
    extra_keys = {"media", "tags", "isAvailable", "groups", "demoComponentRequired"}

    expected = svc_keys | org_keys | meta_keys | extra_keys

    # Execute the actual call
    event    = {"pathParameters": {"orgId": svc.org_id, "serviceId": svc.service_id}}
    response = get_service(event = event,context = None)
    print(response)
    
    assert response["statusCode"] == 200

    data = json.loads(response["body"])["data"]
    print(data)

    assert set(data.keys()) == expected

def test_get_services_success(test_service, db_session):
    event = {}