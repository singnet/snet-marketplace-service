import json
from unittest import TestCase
from datetime import datetime as dt
from unittest.mock import patch
from registry.application.handlers.service_handlers import verify_service_id, save_service, create_service, \
    get_services_for_organization
from registry.infrastructure.repositories.organization_repository import OrganizationRepository
from registry.infrastructure.repositories.service_repository import ServiceRepository
from registry.infrastructure.models.models import Organization, Service, ServiceReviewWorkflow, ServiceGroup, \
    ServiceReviewHistory
from registry.constants import ServiceAvailabilityStatus

org_repo = OrganizationRepository()
service_repo = ServiceRepository()


class TestService(TestCase):
    def setUp(self):
        pass

    def test_verify_service_id(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                name="test_org",
                org_id="test_org_id",
                uuid="test_org_uuid",
                org_type="organization",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                addresses=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        service_repo.add_item(
            Service(
                row_id=1000,
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_ipfs_hash="Qasdfghjklqwertyuiopzxcvbnm",
                proto={},
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                assets={},
                rating={},
                ranking=1,
                contributors=[],
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "queryStringParameters": {"service_id": "test_service_id"}
        }
        response = verify_service_id(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == ServiceAvailabilityStatus.UNAVAILABLE.value)
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "queryStringParameters": {"service_id": "new_test_service_id"}
        }
        response = verify_service_id(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"] == ServiceAvailabilityStatus.AVAILABLE.value)

    def test_create_service(self):
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "POST",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "body": "{}"
        }
        response = create_service(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def test_get_services_for_organization(self):
        self.tearDown()
        org_repo.add_item(
            Organization(
                name="test_org",
                org_id="test_org_id",
                uuid="test_org_uuid",
                org_type="organization",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                addresses=[],
                metadata_ipfs_hash="#dummyhashdummyhash"
            )
        )
        service_repo.add_item(
            Service(
                row_id=1000,
                org_uuid="test_org_uuid",
                uuid="test_service_uuid",
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_ipfs_hash="Qasdfghjklqwertyuiopzxcvbnm",
                proto={},
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                assets={},
                rating={},
                ranking=1,
                contributors=[],
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceReviewWorkflow(
                row_id=1000,
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                state="DRAFT",
                transaction_hash=None,
                created_by="dummy_user",
                updated_by="dummy_user",
                approved_by="dummy_user",
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        service_repo.add_item(
            ServiceGroup(
                row_id="1000",
                org_uuid="test_org_uuid",
                service_uuid="test_service_uuid",
                group_id="test_group_id",
                pricing={},
                endpoints=["https://dummydaemonendpoint.io"],
                created_on=dt.utcnow(),
                updated_on=dt.utcnow()
            )
        )
        event = {
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "GET",
            "pathParameters": {"org_uuid": "test_org_uuid"},
            "body": json.dumps({
                "q": "display",
                "limit": 10,
                "offset": 0,
                "s": "all",
                "sort_by": "display_name",
                "order_by": "desc",
                "filters": []
            })
        }
        response = get_services_for_organization(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        assert (response_body["data"]["total_count"] == 1)
        assert (response_body["data"]["offset"] == 0)
        assert (response_body["data"]["limit"] == 10)
        assert (len(response_body["data"]["result"]) == 1)

    def test_save_service(self):
        event = {
            "path": "/org/test_org_uuid/service",
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "email": "dummy_user1@dummy.io"
                    }
                }
            },
            "httpMethod": "PUT",
            "pathParameters": {"org_uuid": "test_org_uuid", "service_uuid": "test_service_uuid"},
            "body": json.dumps({})
        }
        response = save_service(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def tearDown(self):
        org_repo.session.query(Organization).delete()
        org_repo.session.query(Service).delete()
        org_repo.session.query(ServiceGroup).delete()
        org_repo.session.query(ServiceReviewWorkflow).delete()
        org_repo.session.query(ServiceReviewHistory).delete()
        org_repo.session.commit()
