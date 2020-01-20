import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4

from registry.constants import OrganizationMemberStatus, OrganizationStatus, Role
from registry.consumer.organization_event_consumer import OrganizationCreatedEventConsumer, \
    OrganizationModifiedEventConsumer
from registry.domain.models.group import Group as DomainGroup
from registry.domain.models.organization import Organization as DomainOrganization
from registry.infrastructure.models.models import Group, Organization, OrganizationHistory, OrganizationMember, \
    OrganizationReviewWorkflow
from registry.infrastructure.repositories.organization_repository import OrganizationRepository

ORIGIN = "PUBLISHER_PORTAL"


class TestOrganizationService(unittest.TestCase):

    def setUp(self):
        self.org_repo = OrganizationRepository()

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    def test_organization_create_event(self, nock_read_bytesio_from_ipfs, mock_ipfs_read, mock_s3_push,
                                       mock_ipfs_write):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {'hero_image': {
                "ipfs_hash": 'QmagaSbQAdEtFkwc9ZQUDdYgUtXz93MPByngbx1b4cPidj/484b38d1c1fe4717ad4acab99394ea82-hero_image-20200107083215.png',
                "url": ""}}, "Q3E12", "123456789", ORIGIN,
            [], [DomainGroup(
                name="my-group",
                group_id="group_id",
                payment_address="0x123",
                payment_config={},
                status="",
            )],status=OrganizationStatus.APPROVAL_PENDING.value, owner_name="Dummy Name")

        self.org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISH_IN_PROGRESS.value, username)
        event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
                          'json_str': "{'orgId': b'org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
                          'logIndex': '1', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 44, 9),
                          'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}
        nock_read_bytesio_from_ipfs.return_value = ""
        mock_s3_push.return_value = "http://test-s3-push"
        mock_ipfs_read.return_value = {
            "name": "dummy_org",
            "org_id": "org_id",
            "metadata_ipfs_hash": "Q3E12",
            "org_type": "organization",

            "contacts": [
            ],
            "description": {
                "description": "that is the dummy org for testcases",
                "short_description": "that is the short description",
                "url": "dummy.com"
            },
            "assets": {'hero_image': 'QmagaSbQAdEtFkwc9ZQUDdYgUtXz93MPByngbx1b4cPidj/484b38d1c1fe4717ad4acab99394ea82-hero_image-20200107083215.png'},
            "groups": [{
                "name": "my-group",
                "id": "group_id",
                "payment_address": "0x123",
                "payment_config": {

                }
            }]
        }

        org_event_consumer = OrganizationCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                              "http://ipfs.singularitynet.io",
                                                              80)
        org_event_consumer.on_event(event)
        self.org_repo.session.commit()
        published_org = self.org_repo.get_org_with_status(test_org_id, "PUBLISHED")
        assert len(published_org) == 1
        assert published_org[0].Organization.name == "dummy_org"
        assert published_org[0].Organization.org_id == "org_id"
        assert published_org[0].Organization.type == "organization"
        assert published_org[0].Organization.metadata_ipfs_hash == "Q3E12"
        assert published_org[0].Organization.groups[0].id == "group_id"
        assert published_org[0].Organization.groups[0].name == "my-group"
        assert published_org[0].Organization.groups[0].payment_address == "0x123"

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    def test_organization_modify_event(self, nock_read_bytesio_from_ipfs, mock_ipfs_read, mock_s3_push,
                                       mock_ipfs_write):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "Q3E12",
            "123456789", ORIGIN,
            [], [DomainGroup(
                name="my-group",
                group_id="group_id",
                payment_address="0x123",
                payment_config={},
                status=""
            )], status=OrganizationStatus.APPROVAL_PENDING.value,owner_name="Dummy Name")

        self.org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, username)
        draft_organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "draft_dummy.com", [], {'hero_image': {
                "ipfs_hash": 'QmagaSbQAdEtFkwc9ZQUDdYgUtXz93MPByngbx1b4cPidj/484b38d1c1fe4717ad4acab99394ea82-hero_image-20200107083215.png',
                "url": ""}}, "Q3E12",
            "", ORIGIN, [], [DomainGroup(
                name="my-group",
                group_id="group_id",
                payment_address="0x123",
                payment_config={},
                status=""
            )], status=OrganizationStatus.APPROVAL_PENDING.value,owner_name="Dummy Name")

        self.org_repo.add_org_with_status(draft_organization, OrganizationStatus.PUBLISH_IN_PROGRESS.value, username)

        event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
                          'json_str': "{'orgId': b'org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
                          'logIndex': '1', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 44, 9),
                          'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}
        nock_read_bytesio_from_ipfs.return_value = ""
        mock_s3_push.return_value = "http://test-s3-push"
        mock_ipfs_read.return_value = {
            "name": "dummy_org",
            "org_id": "org_id",
            "metadata_ipfs_hash": "Q3E12",
            "org_type": "organization",

            "contacts": [
            ],
            "description": {
                "description": "that is the dummy org for testcases",
                "short_description": "that is the short description",
                "url": "draft_dummy.com"
            },
            "assets": {'hero_image': 'QmagaSbQAdEtFkwc9ZQUDdYgUtXz93MPByngbx1b4cPidj/484b38d1c1fe4717ad4acab99394ea82-hero_image-20200107083215.png'},
            "groups": [{
                "name": "my-group",
                "id": "group_id",
                "payment_address": "0x123",
                "payment_config": {

                }
            }]
        }

        org_event_consumer = OrganizationModifiedEventConsumer("wss://ropsten.infura.io/ws",
                                                               "http://ipfs.singularitynet.io",
                                                               80)

        self.org_repo.session.commit()
        org_event_consumer.on_event(event)
        self.org_repo.session.commit()
        published_org = self.org_repo.get_org_with_status(test_org_id, "PUBLISHED")
        assert len(published_org) == 1
        assert published_org[0].Organization.name == "dummy_org"
        assert published_org[0].Organization.org_id == "org_id"
        assert published_org[0].Organization.type == "organization"
        assert published_org[0].Organization.metadata_ipfs_hash == "Q3E12"
        assert published_org[0].Organization.groups[0].id == "group_id"
        assert published_org[0].Organization.groups[0].name == "my-group"
        assert published_org[0].Organization.groups[0].payment_address == "0x123"

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    @patch('registry.consumer.organization_event_consumer.OrganizationEventConsumer._get_org_details_from_blockchain')
    def test_organization_member_create_event(self,mock_get_org_details_from_blockchain, nock_read_bytesio_from_ipfs, mock_ipfs_read, mock_s3_push,
                                       mock_ipfs_write):
        test_org_id = uuid4().hex
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {'hero_image': {
                "ipfs_hash": 'QmagaSbQAdEtFkwc9ZQUDdYgUtXz93MPByngbx1b4cPidj/484b38d1c1fe4717ad4acab99394ea82-hero_image-20200107083215.png',
                "url": ""}}, "Q3E12", "123456789", ORIGIN,
            [], [DomainGroup(
                name="my-group",
                group_id="group_id",
                payment_address="0x123",
                payment_config={},
                status="",
            )], status=OrganizationStatus.APPROVAL_PENDING.value, owner_name="Dummy Name")

        self.org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISH_IN_PROGRESS.value, username)
        self.org_repo.add_item(
            OrganizationMember(
                username="user1",
                org_uuid=test_org_id,
                role=Role.MEMBER.value,
                address="member_wallet_address1",
                status=OrganizationMemberStatus.PUBLISH_IN_PROGRESS.value,
                transaction_hash="0x123",
                invite_code="owner_invite_code1"
            )
        )
        self.org_repo.add_item(
            OrganizationMember(
                username="user2",
                org_uuid=test_org_id,
                role=Role.MEMBER.value,
                address="member_wallet_address2",
                status=OrganizationMemberStatus.PUBLISH_IN_PROGRESS.value,
                transaction_hash="0x123",
                invite_code="owner_invite_code2"
            )
        )

        event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
                          'json_str': "{'orgId': b'org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
                          'logIndex': '1', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 44, 9),
                          'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}
        nock_read_bytesio_from_ipfs.return_value = ""
        mock_s3_push.return_value = "http://test-s3-push"
        ipfs_metadata={
            "name": "dummy_org",
            "org_id": "org_id",
            "metadata_ipfs_hash": "Q3E12",
            "org_type": "organization",

            "contacts": [
            ],
            "description": {
                "description": "that is the dummy org for testcases",
                "short_description": "that is the short description",
                "url": "dummy.com"
            },
            "assets": {
                'hero_image': 'QmagaSbQAdEtFkwc9ZQUDdYgUtXz93MPByngbx1b4cPidj/484b38d1c1fe4717ad4acab99394ea82-hero_image-20200107083215.png'},
            "groups": [{
                "name": "my-group",
                "id": "group_id",
                "payment_address": "0x123",
                "payment_config": {

                }
            }]
        }
        mock_ipfs_read.return_value =ipfs_metadata

        mock_get_org_details_from_blockchain.return_value= "org_id",ipfs_metadata,["member_wallet_address1","member_wallet_address3"]

        org_event_consumer = OrganizationCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                              "http://ipfs.singularitynet.io",
                                                              80)
        org_event_consumer.on_event(event)
        self.org_repo.session.commit()
        published_org = self.org_repo.get_org_with_status(test_org_id, "PUBLISHED")
        published_mebers=self.org_repo.get_members_for_given_org_and_status(test_org_id,"PUBLISHED")
        assert len(published_org) == 1
        assert published_org[0].Organization.name == "dummy_org"
        assert published_org[0].Organization.org_id == "org_id"
        assert published_org[0].Organization.type == "organization"
        assert published_org[0].Organization.metadata_ipfs_hash == "Q3E12"
        assert published_org[0].Organization.groups[0].id == "group_id"
        assert published_org[0].Organization.groups[0].name == "my-group"
        assert published_org[0].Organization.groups[0].payment_address == "0x123"
        assert published_mebers[0].address == "member_wallet_address1"
        assert published_mebers[0].status == "PUBLISHED"
        assert published_mebers[1].address == "member_wallet_address3"
        assert published_mebers[1].status == "PUBLISHED"


    def tearDown(self):
        self.org_repo.session.query(Organization).delete()
        self.org_repo.session.query(OrganizationReviewWorkflow).delete()
        self.org_repo.session.query(OrganizationHistory).delete()
        self.org_repo.session.query(Group).delete()

        self.org_repo.session.commit()
