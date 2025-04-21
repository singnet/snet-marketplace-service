import unittest

from registry.infrastructure.models import (
    Organization,
    OrganizationState,
    OrganizationMember,
    OrganizationAddress,
)
from registry.infrastructure.repositories.organization_repository import (
    OrganizationPublisherRepository,
)

ORIGIN = "PUBLISHER"


class TestOrganizationPublisherService(unittest.TestCase):
    def setUp(self):
        self.org_repo = OrganizationPublisherRepository()

    # @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    # @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    # @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    # @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    # @patch('common.blockchain_util.BlockChainUtil')
    # @patch('registry.consumer.organization_event_consumer.OrganizationEventConsumer._get_org_details_from_blockchain')
    # def test_organization_create_event(self, mock_get_org_details_from_blockchain, mock_blockchain_util,
    #                                    mock_read_bytesio_from_ipfs, mock_ipfs_read, mock_s3_push, mock_ipfs_write):
    #     test_org_uuid = uuid4().hex
    #     test_org_id = "org_id"
    #     username = "karl@cryptonian.io"
    #     current_time = datetime.now()
    #     org_state = OrganizationState(
    #         org_uuid=test_org_uuid, state=OrganizationStatus.PUBLISH_IN_PROGRESS.value, transaction_hash="0x123",
    #         test_transaction_hash="0x456", wallet_address="0x987", created_by=username, created_on=current_time,
    #         updated_by=username, updated_on=current_time, reviewed_by="admin", reviewed_on=current_time)

    #     group = Group(
    #         name="default_group", id="group_id", org_uuid=test_org_uuid, payment_address="0x123",
    #         payment_config={
    #             "payment_expiration_threshold": 40320,
    #             "payment_channel_storage_type": "etcd",
    #             "payment_channel_storage_client": {
    #                 "connection_timeout": "5s",
    #                 "request_timeout": "3s", "endpoints": ["http://127.0.0.1:2379"]}}, status="0")

    #     organization = Organization(
    #         uuid=test_org_uuid, name="test_org", org_id=test_org_id, org_type="organization",
    #         origin="PUBLISHER_PORTAL", description="this is long description",
    #         short_description="this is short description", url="https://dummy.com", duns_no="123456789", contacts=[],
    #         assets={"hero_image": {"url": "some_url", "ipfs_hash": "Q123"}},
    #         metadata_uri="Q3E12", org_state=[org_state], groups=[group])
    #     owner = OrganizationMember(
    #         invite_code="123", org_uuid=test_org_uuid, role=Role.OWNER.value, username=username,
    #         status=OrganizationMemberStatus.ACCEPTED.value, address="0x123", created_on=current_time,
    #         updated_on=current_time, invited_on=current_time)
    #     self.org_repo.add_item(organization)
    #     self.org_repo.add_item(owner)
    #     mock_read_bytesio_from_ipfs.return_value = ""
    #     mock_s3_push.return_value = "http://test-s3-push"
    #     ipfs_mock_value = {
    #         "org_name": "test_org",
    #         "org_id": "org_id",
    #         "metadata_ipfs_hash": "Q3E12",
    #         "org_type": "organization",
    #         "contacts": [],
    #         "description": {
    #             "description": "this is long description",
    #             "short_description": "this is short description",
    #             "url": "https://dummy.com"
    #         },
    #         "assets": {
    #             'hero_image': 'Q123'
    #         },
    #         "groups": [{
    #             "group_name": "default_group",
    #             "group_id": "group_id",
    #             "payment": {
    #                 "payment_address": "0x123",
    #                 "payment_expiration_threshold": 40320,
    #                 "payment_channel_storage_type": "etcd",
    #                 "payment_channel_storage_client": {
    #                     "connection_timeout": "5s",
    #                     "request_timeout": "3s",
    #                     "endpoints": [
    #                         "http://127.0.0.1:2379"
    #                     ]
    #                 }
    #             }
    #         }]
    #     }
    #     mock_ipfs_read.return_value = ipfs_mock_value
    #     mock_get_org_details_from_blockchain.return_value = "org_id", ipfs_mock_value, "Q3E12", "0x123", "0x123", []
    #     org_event_consumer = OrganizationCreatedAndModifiedEventConsumer("wss://ropsten.infura.io/ws", self.org_repo)

    #     org_event_consumer.on_event({})
    #     published_org = self.org_repo.get_organization(org_id=test_org_id)
    #     org_owner = self.org_repo.session.query(OrganizationMember).filter(
    #         OrganizationMember.org_uuid == test_org_uuid).filter(OrganizationMember.role == Role.OWNER.value).all()
    #     if len(org_owner) != 1:
    #         assert False
    #     self.assertEqual(org_owner[0].address, "0x123")
    #     self.assertEqual(org_owner[0].username, username)
    #     assert published_org.name == "test_org"
    #     assert published_org.id == "org_id"
    #     assert published_org.org_type == "organization"
    #     assert published_org.metadata_uri == "Q3E12"
    #     assert published_org.groups[0].group_id == "group_id"
    #     assert published_org.groups[0].name == "default_group"
    #     assert published_org.groups[0].payment_address == "0x123"
    #     assert published_org.duns_no == '123456789'
    #     assert published_org.org_state.state == "PUBLISHED"

    # @patch("common.ipfs_util.IPFSUtil", return_value=Mock(write_file_in_ipfs=Mock(return_value="Q3E12")))
    # @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    # @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    # @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    # @patch('common.blockchain_util.BlockChainUtil')
    # @patch('registry.consumer.organization_event_consumer.OrganizationEventConsumer._get_org_details_from_blockchain')
    # def test_organization_create_event_from_snet_cli(self, mock_get_org_details_from_blockchain, mock_block_chain_util,
    #                                                  mock_read_bytesio_from_ipfs,
    #                                                  mock_ipfs_read, mock_s3_push,
    #                                                  mock_ipfs_write):
    #     username = "karl@dummy.com"
    #     test_org_uuid = uuid4().hex
    #     test_org_id = "org_id"
    #     username = "karl@cryptonian.io"

    #     event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
    #                       'json_str': "{'orgId': b'org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
    #                       'processed': b'\x00',
    #                       'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
    #                       'logIndex': '1', 'error_code': 1, 'error_msg': '',
    #                       'row_updated': datetime(2019, 10, 21, 9, 44, 9),
    #                       'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}
    #     mock_read_bytesio_from_ipfs.return_value = ""
    #     mock_s3_push.return_value = "http://test-s3-push"
    #     ipfs_mock_value = {
    #         "org_name": "test_org",
    #         "org_id": "org_id",
    #         "metadata_ipfs_hash": "Q3E12",
    #         "org_type": "organization",

    #         "contacts": [
    #         ],
    #         "description": {
    #             "description": "that is the dummy org for testcases",
    #             "short_description": "that is the short description",
    #             "url": "dummy.com"
    #         },
    #         "assets": {
    #             'hero_image': 'QmagaSbQAdEtFkwc9ZQUDdYgUtXz93MPByngbx1b4cPidj/484b38d1c1fe4717ad4acab99394ea82-hero_image-20200107083215.png'},
    #         "groups": [{
    #             "group_name": "my-group",
    #             "group_id": "group_id",
    #             "payment": {
    #                 "payment_address": "0x123",
    #                 "payment_expiration_threshold": 40320,
    #                 "payment_channel_storage_type": "etcd",
    #                 "payment_channel_storage_client": {
    #                     "connection_timeout": "5s",
    #                     "request_timeout": "3s",
    #                     "endpoints": [
    #                         "http://127.0.0.1:2379"
    #                     ]
    #                 }
    #             }
    #         }]
    #     }
    #     self.org_repo.session.commit()
    #     mock_ipfs_read.return_value = ipfs_mock_value
    #     mock_get_org_details_from_blockchain.return_value = "org_id", ipfs_mock_value, "Q3E12", "79345c7861342442792f6d5a5c7831375c7831645c7866325c7831385c78623661615c7830325c7831635c783838505c7838355c783138775c7831395c7863395c7839315c786563585c786437455c78393821", "0x123", []

    #     org_event_consumer = OrganizationCreatedAndModifiedEventConsumer("wss://ropsten.infura.io/ws", self.org_repo)
    #     org_event_consumer.on_event(event)

    #     published_org = self.org_repo.get_organization(org_id=test_org_id)

    #     assert published_org.name == "test_org"
    #     assert published_org.id == "org_id"
    #     assert published_org.org_type == "organization"
    #     assert published_org.metadata_uri == "Q3E12"

    #     assert published_org.groups[0].group_id == "group_id"
    #     assert published_org.groups[0].name == "my-group"
    #     assert published_org.groups[0].payment_address == "0x123"
    #     assert published_org.org_state.state == OrganizationStatus.PUBLISHED_UNAPPROVED.value

    # @patch("registry.infrastructure.storage_provider.StorageProvider.publish", return_value="ipfs://Q3E12")
    # @patch("registry.infrastructure.storage_provider.StorageProvider.get", return_value="ipfs://Q3E12")
    # @patch("common.s3_util.S3Util.push_io_bytes_to_s3")
    # @patch("common.blockchain_util.BlockChainUtil")
    # @patch("registry.consumer.organization_event_consumer.OrganizationEventConsumer._get_org_details_from_blockchain")
    # def test_organization_owner_change_event(
    #     self,
    #     mock_provider_storage_publish,
    #     mock_provider_storage_get,
    #     mock_s3_push,
    #     blockchain_util,
    #     mock_get_org_details_from_blockchain,
    # ):
    #     username = "karl@dummy.com"
    #     test_org_uuid = uuid4().hex
    #     test_org_id = "org_id"
    #     username = "karl@cryptonian.io"
    #     current_time = datetime.now()
    #     org_state = OrganizationState(
    #         org_uuid=test_org_uuid,
    #         state=OrganizationStatus.PUBLISH_IN_PROGRESS.value,
    #         transaction_hash="0x123",
    #         test_transaction_hash="0x456",
    #         wallet_address="0x987",
    #         created_by=username,
    #         created_on=current_time,
    #         updated_by=username,
    #         updated_on=current_time,
    #         reviewed_by="admin",
    #         reviewed_on=current_time
    #     )

    #     group = Group(
    #         name="default_group", id="group_id", org_uuid=test_org_uuid, payment_address="0x123",
    #         payment_config={
    #             "payment_expiration_threshold": 40320,
    #             "payment_channel_storage_type": "etcd",
    #             "payment_channel_storage_client": {
    #                 "connection_timeout": "5s",
    #                 "request_timeout": "3s", "endpoints": ["http://127.0.0.1:2379"]
    #             }
    #         },
    #         status="0"
    #     )

    #     organization = Organization(
    #         uuid=test_org_uuid,
    #         name="test_org",
    #         org_id=test_org_id,
    #         org_type="organization",
    #         origin="PUBLISHER_PORTAL",
    #         description="this is long description",
    #         short_description="this is short description", url="https://dummy.com", duns_no="123456789", contacts=[],
    #         assets={
    #             "hero_image":
    #             {
    #                 "url": "some_url",
    #                 "ipfs_hash": "ipfs://Q123"
    #             }
    #         },
    #         metadata_uri="ipfs://Q3E12",
    #         org_state=[org_state],
    #         groups=[group]
    #     )
    #     owner = OrganizationMember(
    #         invite_code="123",
    #         org_uuid=test_org_uuid,
    #         role=Role.OWNER.value,
    #         username=username,
    #         status=OrganizationMemberStatus.PUBLISHED.value,
    #         address="0x123",
    #         created_on=current_time,
    #         updated_on=current_time,
    #         invited_on=current_time
    #     )
    #     self.org_repo.add_item(organization)
    #     self.org_repo.add_item(owner)
    #     event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
    #                       'json_str': "{'orgId': b'org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
    #                       'processed': b'\x00',
    #                       'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
    #                       'logIndex': '1', 'error_code': 1, 'error_msg': '',
    #                       'row_updated': datetime(2019, 10, 21, 9, 44, 9),
    #                       'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}
    #     mock_s3_push.return_value = "http://test-s3-push"
    #     ipfs_mock_value = {
    #         "org_name": "test_org",
    #         "org_id": "org_id",
    #         "org_type": "organization",
    #         "contacts": [
    #         ],
    #         "description": {
    #             "description": "this is long description",
    #             "short_description": "this is short description",
    #             "url": "https://dummy.com"
    #         },
    #         "assets": {
    #             'hero_image': 'Q123'},
    #         "groups": [{
    #             "group_name": "default_group",
    #             "group_id": "group_id",
    #             "payment": {
    #                 "payment_address": "0x123",
    #                 "payment_expiration_threshold": 40320,
    #                 "payment_channel_storage_type": "etcd",
    #                 "payment_channel_storage_client": {
    #                     "connection_timeout": "5s",
    #                     "request_timeout": "3s",
    #                     "endpoints": [
    #                         "http://127.0.0.1:2379"
    #                     ]
    #                 }
    #             }
    #         }]
    #     }
    #     self.org_repo.session.commit()
    #     mock_provider_storage_get.return_value = ipfs_mock_value
    #     mock_get_org_details_from_blockchain.return_value = "org_id", ipfs_mock_value, "ipfs://Q3E12", "79345c7861342442792f6d5a5c7831375c7831645c7866325c7831385c78623661615c7830325c7831635c783838505c7838355c783138775c7831395c7863395c7839315c786563585c786437455c78393821", "0x1234", []
    #     org_event_consumer = OrganizationCreatedAndModifiedEventConsumer("wss://ropsten.infura.io/ws", self.org_repo)

    #     org_event_consumer.on_event({})
    #     published_org = self.org_repo.get_organization(org_id=test_org_id)
    #     owner = self.org_repo.session.query(OrganizationMember).filter(
    #         OrganizationMember.org_uuid == test_org_uuid).filter(OrganizationMember.role == Role.OWNER.value).all()
    #     if len(owner) != 1:
    #         assert False
    #     self.assertEqual(owner[0].address, "0x1234")
    #     self.assertEqual(owner[0].username, "")

    #     assert published_org.name == "test_org"
    #     assert published_org.id == "org_id"
    #     assert published_org.org_type == "organization"
    #     assert published_org.metadata_uri == "ipfs://Q3E12"
    #     assert published_org.groups[0].group_id == "group_id"
    #     assert published_org.groups[0].name == "default_group"
    #     assert published_org.groups[0].payment_address == "0x123"
    #     assert published_org.duns_no == "123456789"
    #     assert published_org.org_state.state == "PUBLISHED"

    def tearDown(self):
        self.org_repo.session.query(Organization).delete()
        self.org_repo.session.query(OrganizationState).delete()
        self.org_repo.session.query(OrganizationMember).delete()
        self.org_repo.session.query(OrganizationAddress).delete()
        self.org_repo.session.commit()
