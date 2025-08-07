from unittest import TestCase

from contract_api.domain.models.organization import NewOrganizationDomain
from contract_api.domain.models.service import NewServiceDomain
from contract_api.infrastructure.repositories.organization_repository import OrganizationRepository
from contract_api.infrastructure.repositories.service_repository import ServiceRepository
from contract_api.application.handlers.dapp_build_handlers import notify_deploy_status


class TestDappBuild(TestCase):

    def setUp(self):
        self.org_repository = OrganizationRepository()
        self.service_repository = ServiceRepository()
        self.org_repository.upsert_organization(
            NewOrganizationDomain(
                org_id = "test_org_id",
                organization_name = "test_org_name",
                owner_address = "0x6E7BaCcc00D69eab750eDf661D831cd2c7f3A4DF",
                org_metadata_uri = "",
                org_assets_url = {"hero_image": "test_url"},
                is_curated = True,
                description = {},
                assets_hash = {},
                contacts = {},
            )
        )
        self.org_repository.session.commit()
        self.service_repository.upsert_service(
            NewServiceDomain(
                org_id = "test_org_id",
                service_id = "test_service_id",
                hash_uri = "",
                is_curated = False
            )
        )
        self.service_repository.session.commit()

    def tearDown(self):
        self.service_repository.delete_service(
            "test_org_id", "test_service_id"
        )

    def test_notify_deploy_status(self):
        event = {
            "org_id": "test_org_id",
            "service_id": "test_service_id",
            "build_status": "1"
        }

        response = notify_deploy_status(event = event, context = None)
        assert response["statusCode"] == 201

        assert self.service_repository.service_curated("test_org_id", "test_service_id")
