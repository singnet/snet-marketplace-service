import unittest

from registry.domain.services.organization_service import OrganizationService
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class TestOrganizationService(unittest.TestCase):

    def setUp(self):
        self.repository = OrganizationRepository()

    def test_add_org_draft(self):
        payload = {
            "org_id": "org_dummy",
            "org_name": "dummy_org",
            "org_type": "individual",
            "description": "this is the dummy org for testcases",
            "short_description": "this is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {},
            "groups": [
                {
                    "id": "2134",
                    "name": "dummy_group",
                    "payment_address": "0x123",
                    "payment_config": {}
                }
            ]

        }
        username = "dummy@dummy.com"
        OrganizationService().add_organization_draft(payload, username)
        organizations = self.repository.get_org_latest_from_org_id("org_dummy")
        if len(organizations) > 0:
            assert organizations[0].status == "DRAFT"

    def tearDown(self):
        pass
