import json
import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4

from common.exceptions import OperationNotAllowed
from common.utils import datetime_to_string
from registry.application.handlers.organization_handlers import update_org
from registry.application.services.organization_publisher_service import OrganizationPublisherService, org_repo
from registry.constants import OrganizationStatus, OrganizationActions, OrganizationType, OrganizationMemberStatus, \
    Role, OrganizationAddressType
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.models.organization import Organization as DomainOrganization
from registry.infrastructure.models import Organization, OrganizationMember, OrganizationState, Group, \
    OrganizationAddress
from registry.testcases.test_variables import ORG_GROUPS, ORG_PAYLOAD_MODEL, \
    ORG_RESPONSE_MODEL, ORG_ADDRESS, ORIGIN

ORG_PAYLOAD_REQUIRED_KEYS = ["org_id", "org_uuid", "org_name", "origin", "org_type", "metadata_uri",
                             "description", "short_description", "url", "contacts", "assets",
                             "mail_address_same_hq_address", "addresses", "duns_no"]


class TestOrganizationPublisherService(unittest.TestCase):

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_create_organization(self, mock_boto, mock_ipfs):
        username = "karl@cryptonian.io"
        payload = {
            "org_id": "", "org_uuid": "", "org_name": "test_org", "org_type": "organization",
            "metadata_uri": "", "duns_no": "123456789", "origin": ORIGIN, "description": "",
            "short_description": "", "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_hash": ""}},
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
    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_edit_organization_after_change_requested(self, mock_invoke_lambda, mock_boto,
                                                      mock_ipfs):
        username = "karl@dummy.com"
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        groups = OrganizationFactory.group_domain_entity_from_group_list_payload(json.loads(ORG_GROUPS))
        org_repo.add_organization(
            DomainOrganization(test_org_uuid, test_org_id, "org_dummy", OrganizationType.INDIVIDUAL.value, ORIGIN, "",
                               "",
                               "", [], {}, "", "", groups, [], [], []),
            username, OrganizationStatus.CHANGE_REQUESTED.value)
        payload = json.loads(ORG_PAYLOAD_MODEL)
        payload["org_uuid"] = test_org_uuid
        payload["org_id"] = test_org_id
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
        self.assertDictEqual.__self__.maxDiff = None
        self.assertDictEqual(expected_organization, org_dict)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_edit_organization_with_org_id(self, mock_boto, mock_ipfs):
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
        self.assertEqual("OK", OrganizationPublisherService(test_org_uuid, username)
                         .update_organization(payload, OrganizationActions.DRAFT.value))

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_submit_organization_for_approval_after_published(self, mock_boto, mock_ipfs):
        username = "karl@dummy.com"
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        payload = {
            "org_id": test_org_id, "org_uuid": test_org_uuid, "org_name": "test_org", "org_type": "organization",
            "metadata_uri": "", "duns_no": "123456789", "origin": ORIGIN,
            "description": "this is description", "short_description": "this is short description",
            "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_hash": ""}},
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
    def test_publish_organization_after_published(self, mock_boto, mock_ipfs):
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        current_time = datetime.now()
        org_state = OrganizationState(
            org_uuid=test_org_uuid, state=OrganizationStatus.APPROVED.value, transaction_hash="0x123",
            test_transaction_hash="0x456", wallet_address="0x987", created_by=username, created_on=current_time,
            updated_by=username, updated_on=current_time, reviewed_by="admin", reviewed_on=current_time)

        group = Group(
            name="default_group", id="group_id", org_uuid=test_org_uuid, payment_address="0x123",
            payment_config={
                "payment_expiration_threshold": 40320,
                "payment_channel_storage_type": "etcd",
                "payment_channel_storage_client": {
                    "connection_timeout": "5s",
                    "request_timeout": "3s", "endpoints": ["http://127.0.0.1:2379"]}}, status="0")
        org_address = [OrganizationAddress(
            org_uuid=test_org_uuid, address_type=OrganizationAddressType.HEAD_QUARTER_ADDRESS.value,
            street_address="F102", apartment="ABC Apartment", city="TestCity", pincode="123456",
            state="state", country="TestCountry"),
            OrganizationAddress(
                org_uuid=test_org_uuid, address_type=OrganizationAddressType.MAIL_ADDRESS.value,
                street_address="F102", apartment="ABC Apartment", city="TestCity", pincode="123456",
                state="state", country="TestCountry")
        ]

        organization = Organization(
            uuid=test_org_uuid, name="test_org", org_id=test_org_id, org_type="organization",
            origin=ORIGIN, description="this is long description",
            short_description="this is short description", url="https://dummy.com", duns_no="123456789", contacts=[],
            assets={"hero_image": {"url": "some_url", "ipfs_hash": "Q123"}},
            metadata_uri="Q3E12", org_state=[org_state], groups=[group], addresses=org_address)

        owner = OrganizationMember(
            invite_code="123", org_uuid=test_org_uuid, role=Role.OWNER.value, username=username,
            status=OrganizationMemberStatus.ACCEPTED.value, address="0x123", created_on=current_time,
            updated_on=current_time, invited_on=current_time)
        org_repo.add_item(organization)
        org_repo.add_item(owner)
        event = {
            "pathParameters": {"org_uuid": test_org_uuid},
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "queryStringParameters": {"action": "DRAFT"},
            "body": json.dumps({
                "org_id": test_org_id, "org_uuid": test_org_uuid, "org_name": "test_org", "org_type": "organization",
                "metadata_uri": "", "duns_no": "123456789", "origin": ORIGIN,
                "description": "this is long description",
                "short_description": "this is short description",
                "url": "https://dummy.com", "contacts": [],
                "assets": {"hero_image": {"url": "https://my_image", "ipfs_hash": ""}},
                "org_address": ORG_ADDRESS, "groups": [{
                    "name": "default",
                    "id": "group_id",
                    "payment_address": "0x123",
                    "payment_config": {
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "1s",
                            "request_timeout": "1s",
                            "endpoints": [
                                "123"
                            ]
                        }
                    }
                }],
                "state": {}
            })
        }
        update_org(event, None)
        updated_org = org_repo.get_organization(org_id=test_org_id)
        owner = org_repo.session.query(OrganizationMember).filter(
            OrganizationMember.org_uuid == test_org_uuid).filter(OrganizationMember.role == Role.OWNER.value).all()
        if len(owner) != 1:
            assert False
        assert updated_org.name == "test_org"
        assert updated_org.id == "org_id"
        assert updated_org.org_type == "organization"
        assert updated_org.metadata_uri == ""
        assert updated_org.groups[0].group_id == "group_id"
        assert updated_org.groups[0].name == "default"
        assert updated_org.groups[0].payment_address == "0x123"
        assert updated_org.duns_no == '123456789'
        assert updated_org.org_state.state == OrganizationStatus.APPROVED.value

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_submit_organization_for_approval_after_approved(self, mock_boto, mock_ipfs):
        username = "karl@dummy.com"
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        payload = {
            "org_id": test_org_id, "org_uuid": test_org_uuid, "org_name": "test_org", "org_type": "organization",
            "metadata_uri": "", "duns_no": "123456789", "origin": ORIGIN,
            "description": "this is description", "short_description": "this is short description",
            "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_hash": ""}},
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
            "metadata_uri": "", "duns_no": "123456789", "origin": ORIGIN,
            "description": "this is description", "short_description": "this is short description",
            "url": "https://dummy.dummy", "contacts": "",
            "assets": {"hero_image": {"url": "", "ipfs_hash": ""}},
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
            if org_db_model.org_state[0].state == OrganizationStatus.ONBOARDING_APPROVED.value:
                assert True
            else:
                assert False

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q12PWP")))
    @patch("registry.domain.models.organization.json_to_file")
    def test_org_publish_to_ipfs(self, mock_json_to_file_util, mock_ipfs_utils):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        org_repo.add_organization(
            DomainOrganization(test_org_id, "org_id", "org_dummy", OrganizationType.ORGANIZATION.value, ORIGIN, "", "",
                               "", [], {}, "", "", [], [], [], []),
            username, OrganizationStatus.APPROVED.value)
        response = OrganizationPublisherService(test_org_id, username).publish_organization()
        self.assertEqual(response["metadata_uri"], "ipfs://Q12PWP")

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q12PWP")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_org_verification_individual(self, mock_boto_utils, mock_ipfs_utils):
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
            "INDIVIDUAL", verification_details={"updated_by": "TEST_CASES", "status": "APPROVED", "username": username})
        organization = org_repo.get_organizations(OrganizationStatus.ONBOARDING_APPROVED.value)
        self.assertEqual(len(organization), 3)

    @patch("common.utils.send_email_notification")
    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q12PWP")))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(s3_upload_file=Mock()))
    def test_org_verification_organization(self, mock_boto_utils, mock_ipfs_utils, mock_email):
        username = "karl@dummy.in"
        org_id = "test_org_id"
        org_uuid = "test_org_uuid"
        org_repo.add_organization(DomainOrganization(org_uuid, org_id, f"org_{org_id}",
                                                     OrganizationType.ORGANIZATION.value, ORIGIN, "",
                                                     "", "", [], {}, "", "", [], [], [], []),
                                  username, OrganizationStatus.ONBOARDING.value)

        OrganizationPublisherService(None, None).update_verification(
            "DUNS", verification_details={"updated_by": "TEST_CASES", "comment": "approved",
                                          "status": "APPROVED", "org_uuid": org_uuid})
        organization = org_repo.get_organizations(OrganizationStatus.ONBOARDING_APPROVED.value)
        self.assertEqual(len(organization), 1)

    def tearDown(self):
        org_repo.session.query(Group).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(OrganizationState).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Organization).delete()
        org_repo.session.commit()