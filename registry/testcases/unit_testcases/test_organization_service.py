import unittest
from unittest.mock import patch, Mock

from registry.domain.services.organization_service import OrganizationService
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class TestOrganizationService(unittest.TestCase):

    def setUp(self):
        self.org_repo = OrganizationRepository()

    def test_add_new_org_draft(self):
        payload = {
            "org_id": "org_dummy",
            "org_uuid": "",
            "org_name": "dummy_org",
            "org_type": "individual",
            "metadata_ipfs_hash": "",
            "description": "that is the dummy org for testcases",
            "short_description": "that is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {}
        }
        username = "pratik@dummy.com"
        organizaiton = OrganizationService().add_organization_draft(payload, username)
        test_org_id = organizaiton["org_uuid"]


        payload = {
            "org_id": "org_dummy",
            "org_name": "dummy_org",
            "org_type": "individual",
            "org_uuid": test_org_id,
            "description": "this is the dummy org for testcases",
            "short_description": "this is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {}
        }
        username = "dummy@dummy.com"
        OrganizationService().add_organization_draft(payload, username)
        self.org_repo
        assert True

    # def submit_org_for_approval(self):
    #     pass
    #
    # @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    # def test_publish_org_ipfs(self, ipfs_mock):
    #     OrganizationService().publish_org("184bd22274de45ae9feda73598086fd8", "pratik@dummy.io")
    #
    # def test_get_org_for_username(self):
    #     username = "dummy@dummy.io"
    #     OrganizationService().get_organizations_for_user(username)
    #
    # def test_get_organizations(self):
    #     OrganizationService().get_organization()


    def tearDown(self):
        pass
