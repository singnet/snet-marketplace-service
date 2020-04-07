import json
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from registry.application.services.organization_publisher_service import OrganizationPublisherService, org_repo
from registry.constants import OrganizationStatus, OrganizationActions, OrganizationType
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.models.organization import Organization as DomainOrganization
from registry.infrastructure.models import Organization, OrganizationMember, OrganizationState, Group, \
    OrganizationAddress
from registry.testcases.test_variables import ORG_GROUPS, ORG_PAYLOAD_MODEL, \
    ORG_RESPONSE_MODEL, ORG_ADDRESS, ORIGIN

ORG_PAYLOAD_REQUIRED_KEYS = ["org_id", "org_uuid", "org_name", "origin", "org_type", "metadata_ipfs_uri",
                             "description", "short_description", "url", "contacts", "assets",
                             "mail_address_same_hq_address", "addresses", "duns_no"]


class TestOrganizationPublisherService(unittest.TestCase):

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_create_organization(self, mock_boto, mock_ipfs):
        username = "karl@cryptonian.io"
        payload = {
            "org_id": "", "org_uuid": "", "org_name": "test_org", "org_type": "organization",
            "metadata_ipfs_uri": "", "duns_no": "123456789", "origin": ORIGIN,
            "description": "", "short_description": "", "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_uri": ""}},
            "org_address": ORG_ADDRESS, "groups": json.loads(ORG_GROUPS),
            "state": {}
        }
        response = OrganizationPublisherService(None, username).create_organization(payload)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is not None:
            assert True
        else:
            assert False

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_edit_organization(self, mock_boto, mock_ipfs):
        username = "karl@dummy.com"
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        groups = OrganizationFactory.group_domain_entity_from_group_list_payload(json.loads(ORG_GROUPS))
        org_repo.add_organization(
            DomainOrganization(test_org_uuid, test_org_id, "org_dummy", "ORGANIZATION", ORIGIN, "", "",
                               "", [], {}, "", "", groups, [], [], []),
            username, OrganizationStatus.PUBLISHED.value)
        payload = json.loads(ORG_PAYLOAD_MODEL)
        payload["org_uuid"] = test_org_uuid
        OrganizationPublisherService(test_org_uuid, username) \
            .update_organization(payload, OrganizationActions.DRAFT.value)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        organization = OrganizationFactory.org_domain_entity_from_repo_model(org_db_model)
        org_dict = organization.to_response()
        org_dict["state"] = {}
        org_dict["groups"] = []
        org_dict["assets"]["hero_image"]["url"] = ""
        expected_organization = json.loads(ORG_RESPONSE_MODEL)
        expected_organization["org_id"] = test_org_id
        expected_organization["groups"] = []
        expected_organization["org_uuid"] = test_org_uuid
        self.assertDictEqual(expected_organization, org_dict)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_submit_organization_for_approval_after_published(self, mock_boto, mock_ipfs):
        username = "karl@dummy.com"
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        payload = {
            "org_id": test_org_id, "org_uuid": test_org_uuid, "org_name": "test_org", "org_type": "organization",
            "metadata_ipfs_uri": "", "duns_no": "123456789", "origin": ORIGIN,
            "description": "this is description", "short_description": "this is short description",
            "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_uri": ""}},
            "org_address": ORG_ADDRESS, "groups": json.loads(ORG_GROUPS),
            "state": {}
        }
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        org_repo.add_organization(organization, username, OrganizationStatus.PUBLISHED.value)
        OrganizationPublisherService(test_org_uuid, username) \
            .update_organization(payload, OrganizationActions.SUBMIT.value)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        else:
            if org_db_model.org_state[0].state == OrganizationStatus.APPROVED.value:
                assert True
            else:
                assert False


    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_submit_organization_for_approval_after_approved(self, mock_boto, mock_ipfs):
        username = "karl@dummy.com"
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        payload = {
            "org_id": test_org_id, "org_uuid": test_org_uuid, "org_name": "test_org", "org_type": "organization",
            "metadata_ipfs_uri": "", "duns_no": "123456789", "origin": ORIGIN,
            "description": "this is description", "short_description": "this is short description",
            "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_uri": ""}},
            "org_address": ORG_ADDRESS, "groups": json.loads(ORG_GROUPS),
            "state": {}
        }
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        org_repo.add_organization(organization, username, OrganizationStatus.APPROVED.value)
        OrganizationPublisherService(test_org_uuid, username) \
            .update_organization(payload, OrganizationActions.SUBMIT.value)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        else:
            if org_db_model.org_state[0].state == OrganizationStatus.APPROVED.value:
                assert True
            else:
                assert False

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_submit_organization_for_approval_after_onboarding_approved(self, mock_boto, mock_ipfs):
        username = "karl@dummy.com"
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        payload = {
            "org_id": test_org_id, "org_uuid": test_org_uuid, "org_name": "test_org", "org_type": "organization",
            "metadata_ipfs_uri": "", "duns_no": "123456789", "origin": ORIGIN,
            "description": "this is description", "short_description": "this is short description",
            "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_uri": ""}},
            "org_address": ORG_ADDRESS, "groups": json.loads(ORG_GROUPS),
            "state": {}
        }
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        org_repo.add_organization(organization, username, OrganizationStatus.ONBOARDING_APPROVED.value)
        OrganizationPublisherService(test_org_uuid, username) \
            .update_organization(payload, OrganizationActions.SUBMIT.value)
        org_db_model = org_repo.session.query(Organization).first()
        if org_db_model is None:
            assert False
        else:
            if org_db_model.org_state[0].state == OrganizationStatus.APPROVED.value:
                assert True
            else:
                assert False

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q12PWP")))
    @patch("registry.domain.services.registry_blockchain_util."
           "RegistryBlockChainUtil.publish_organization_to_test_network", return_value="0x123")
    @patch("registry.domain.models.organization.json_to_file")
    def test_org_publish_to_ipfs(self, mock_json_to_file_util, mock_test_network_publish, mock_ipfs_utils):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        org_repo.add_organization(
            DomainOrganization(test_org_id, "org_id", "org_dummy", "ORGANIZATION", ORIGIN, "", "",
                               "", [], {}, "", "", [], [], [], []),
            username, OrganizationStatus.APPROVED.value)
        response = OrganizationPublisherService(test_org_id, username).publish_org_to_ipfs()
        self.assertEqual(response["metadata_ipfs_uri"], "ipfs://Q12PWP")

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q12PWP")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_org_verification(self, mock_boto_utils, mock_ipfs_utils):
        username = "karl@dummy.in"
        for count in range(0, 3):
            org_id = uuid4().hex
            org_repo.add_organization(DomainOrganization(org_id, org_id, f"org_{org_id}",
                                                         OrganizationType.INDIVIDUAL.value, ORIGIN, "",
                                                         "", "", [], {}, "", "", [], [], [], []),
                                      username, OrganizationStatus.ONBOARDING.value)
        for count in range(0, 3):
            org_id = uuid4().hex
            org_repo.add_organization(DomainOrganization(org_id, org_id, f"org_{org_id}",
                                                         OrganizationType.INDIVIDUAL.value, ORIGIN, "",
                                                         "", "", [], {}, "", "", [], [], [], []),
                                      username, OrganizationStatus.APPROVED.value)
        OrganizationPublisherService(None, None).update_verification(
            "JUMIO", verification_details={"updated_by": "TEST_CASES", "status": "APPROVED", "username": username})
        organization = org_repo.get_org(OrganizationStatus.ONBOARDING_APPROVED.value)
        self.assertEqual(len(organization), 3)

    def tearDown(self):
        org_repo.session.query(Group).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(OrganizationState).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Organization).delete()
        org_repo.session.commit()
