import unittest

from registry.domain.services.organization_service import OrganizationService


class TestOrganizationService(unittest.TestCase):

    def setUp(self):
        # self.repository = OrganizationRepository()
        pass

    def test_add_new_org_draft(self):
        payload = {
            "org_id": "org_dummy",
            "org_uuid": "c8494b71dca1469f931686bf3798ab14",
            "org_name": "dummy_org",
            "org_type": "individual",
            "metadata_ipfs_hash": "",
            "description": "this is the dummy org for testcases",
            "short_description": "that is the short description",
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
        assert True

    def test_update_draft(self):
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
        assert True

    def test_get_org_for_username(self):
        username = "dummy@dummy.io"
        OrganizationService().get_organizations_for_user(username)

    def test_get_organizations(self):
        OrganizationService().get_organization()

    def test_publish_org_ipfs(self):
        OrganizationService().publish_org_ipfs("c8494b71dca1469f931686bf3798ab14")

    def tearDown(self):
        pass
