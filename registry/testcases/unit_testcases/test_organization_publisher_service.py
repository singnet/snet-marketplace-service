import json
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
from registry.application.services.organization_publisher_service import OrganizationPublisherService, org_repo
from registry.constants import OrganizationStatus, Role
from registry.domain.models.organization import Organization as DomainOrganization
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.models import Organization, OrganizationMember, OrganizationState, Group, \
    OrganizationAddress
from registry.testcases.test_variables import RAW_IMAGE_FILE, ORG_ADDRESS, ORG_GROUPS, ORG_PAYLOAD_MODEL, \
    ORG_RESPONSE_MODEL

ORIGIN = "PUBLISHER_DAPP"
ORG_PAYLOAD_REQUIRED_KEYS = ["org_id", "org_uuid", "org_name", "origin", "org_type", "metadata_ipfs_hash",
                             "description", "short_description", "url", "contacts", "assets",
                             "mail_address_same_hq_address", "addresses", "duns_no"]


class TestOrganizationPublisherService(unittest.TestCase):

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_add_organization_draft(self, mock_boto, mock_ipfs):
        username = "dummy@dummy.com"
        payload = json.loads(ORG_PAYLOAD_MODEL)
        payload["assets"]["hero_image"]["raw"] = RAW_IMAGE_FILE
        payload["assets"]["hero_image"]["file_type"] = "jpg"
        OrganizationPublisherService(None, username).add_organization_draft(payload)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        organization = OrganizationFactory.org_domain_entity_from_repo_model(org_db_model)
        test_org_uuid = organization.uuid
        test_org_id = organization.id
        org_dict = organization.to_dict()
        org_dict["state"] = {}
        org_dict["assets"]["hero_image"]["url"] = ""
        expected_organization = json.loads(ORG_RESPONSE_MODEL)
        expected_organization["org_id"] = test_org_id
        expected_organization["org_uuid"] = test_org_uuid
        self.assertDictEqual(expected_organization, org_dict)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_add_organization_draft_update(self, mock_boto, mock_ipfs):
        username = "dummy@dummy.com"
        payload = json.loads(ORG_PAYLOAD_MODEL)
        payload["assets"]["hero_image"]["raw"] = RAW_IMAGE_FILE
        payload["assets"]["hero_image"]["file_type"] = "jpg"
        OrganizationPublisherService(None, username).add_organization_draft(payload)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        organization = OrganizationFactory.org_domain_entity_from_repo_model(org_db_model)
        test_org_uuid = organization.uuid
        test_org_id = organization.id
        org_dict = organization.to_dict()
        org_dict["state"] = {}
        org_dict["assets"]["hero_image"]["url"] = ""
        expected_organization = json.loads(ORG_RESPONSE_MODEL)
        expected_organization["org_id"] = test_org_id
        expected_organization["org_uuid"] = test_org_uuid
        payload["org_id"] = test_org_id
        payload["org_uuid"] = test_org_uuid
        payload["short_description"] = "new"
        expected_organization["short_description"] = "new"
        OrganizationPublisherService(None, username).add_organization_draft(payload)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        organization = OrganizationFactory.org_domain_entity_from_repo_model(org_db_model)
        org_dict = organization.to_dict()
        org_dict["state"] = {}
        org_dict["assets"]["hero_image"]["url"] = ""
        self.assertDictEqual(expected_organization, org_dict)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_submit_org_for_approval(self, mock_boto_utils, mock_ipfs_utils):
        username = "dummy@dummy.com"
        payload = json.loads(ORG_PAYLOAD_MODEL)
        payload["assets"]["hero_image"]["raw"] = RAW_IMAGE_FILE
        payload["assets"]["hero_image"]["file_type"] = "jpg"
        OrganizationPublisherService(None, username).submit_org_for_approval(payload)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        organization = OrganizationFactory.org_domain_entity_from_repo_model(org_db_model)
        test_org_uuid = organization.uuid
        test_org_id = organization.id
        org_dict = organization.to_dict()
        org_dict["state"] = {"state": org_dict["state"]["state"]}
        org_dict["assets"]["hero_image"]["url"] = ""
        expected_organization = json.loads(ORG_RESPONSE_MODEL)
        expected_organization["org_id"] = test_org_id
        expected_organization["org_uuid"] = test_org_uuid
        expected_organization["state"]["state"] = OrganizationStatus.APPROVAL_PENDING.value
        self.assertDictEqual(expected_organization, org_dict)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    def test_org_publish_to_ipfs(self, mock_ipfs_utils):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        org_repo.add_organization(
            DomainOrganization(test_org_id, "org_id", "org_dummy", "ORGANIZATION", ORIGIN, "", "",
                               "", [], {}, "", "", [], [], [], []),
            username, OrganizationStatus.APPROVED.value)
        response = OrganizationPublisherService(test_org_id, username).publish_org_to_ipfs()
        self.assertEqual(response["metadata_ipfs_hash"], "Q3E12")

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_get_group_for_org(self, mock_boto_utils, mock_ipfs_utils):
        username = "dummy@dummy.com"
        payload = json.loads(ORG_PAYLOAD_MODEL)
        payload["assets"]["hero_image"]["raw"] = RAW_IMAGE_FILE
        payload["assets"]["hero_image"]["file_type"] = "jpg"
        OrganizationPublisherService(None, username).add_organization_draft(payload)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        organization = OrganizationFactory.org_domain_entity_from_repo_model(org_db_model)
        test_org_uuid = organization.uuid
        group_response = OrganizationPublisherService(test_org_uuid, username).get_groups_for_org()
        self.assertDictEqual(group_response, {"org_uuid": test_org_uuid, "groups": json.loads(ORG_GROUPS)})


    def tearDown(self):
        org_repo.session.query(Group).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(OrganizationState).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Organization).delete()
        org_repo.session.commit()
