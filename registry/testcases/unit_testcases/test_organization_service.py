import unittest
from unittest.mock import patch, Mock
from uuid import uuid4

from registry.domain.services.organization_service import OrganizationService
from registry.domain.models.organization import Organization as DomainOrganization
from registry.infrastructure.models.models import Organization, OrganizationReviewWorkflow, OrganizationHistory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class TestOrganizationService(unittest.TestCase):

    def setUp(self):
        self.org_service = OrganizationService()
        self.org_repo = OrganizationRepository()

    def test_add_new_org_draft_one(self):
        """
        Add organization draft with type individual, org_id wont be given
        """
        payload = {
            "org_id": "",
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
        response_org = OrganizationService().add_organization_draft(payload, username)
        test_org_id = response_org["org_uuid"]

        orgs = self.org_repo.get_organization_draft(test_org_id)
        if len(orgs) == 0:
            assert False
        else:
            self.assertEqual(orgs[0].org_uuid, test_org_id)

        payload = {
            "org_id": "test_org_id",
            "org_name": "dummy_org",
            "org_type": "individual",
            "org_uuid": test_org_id,
            "description": "this is the dummy org for testcases",
            "short_description": "that is the short description",
            "url": "https://dummy.dummy",
            "contacts": [],
            "assets": {}
        }
        username = "dummy@dummy.com"
        OrganizationService().add_organization_draft(payload, username)
        orgs = self.org_repo.get_organization_draft(test_org_id)
        if len(orgs) == 0:
            assert False
        else:
            self.assertEqual(orgs[0].org_uuid, test_org_id)
            self.assertEqual(orgs[0].short_description, "that is the short description")

    def test_add_new_org_draft_two(self):
        """
        Add organization draft without org id with type "organization"
        """
        payload = {
            "org_id": "",
            "org_uuid": "",
            "org_name": "dummy_org",
            "org_type": "organization",
            "metadata_ipfs_hash": "",
            "description": "",
            "short_description": "",
            "url": "",
            "contacts": [],
            "assets": {}
        }
        username = "pratik@dummy.com"
        self.assertRaises(Exception, OrganizationService().add_organization_draft, payload, username)

    def test_submit_org_for_approval(self):
        payload = {
            "org_id": "",
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
        response_org = self.org_service.add_organization_draft(payload, username)
        test_org_id = response_org["org_uuid"]

        self.org_service.submit_org_for_approval(test_org_id, "dummy@snet.io")

        orgs = self.org_repo.get_org_with_status(test_org_id, "APPROVAL_PENDING")
        if len(orgs) == 0:
            assert False
        else:
            self.assertEqual(orgs[0].OrganizationReviewWorkflow.updated_by, "dummy@snet.io")

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    def test_publish_org_ipfs(self, ipfs_mock):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        self.org_repo.add_org_with_status(DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization",
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], [], ""),
            "APPROVED", username)
        response = OrganizationService().publish_org(test_org_id, username)
        self.assertEqual(response["metadata_ipfs_hash"], "Q3E12")

        orgs = self.org_repo.get_org_with_status(test_org_id, "PUBLISH_IN_PROGRESS")
        if len(orgs) == 0:
            assert False
        else:
            self.assertEqual(orgs[0].OrganizationReviewWorkflow.updated_by, username)

    def tearDown(self):
        self.org_repo.session.query(Organization).delete()
        self.org_repo.session.query(OrganizationReviewWorkflow).delete()
        self.org_repo.session.query(OrganizationHistory).delete()
        self.org_repo.session.commit()
