import json
import unittest
from datetime import datetime
from random import randrange
from unittest.mock import patch, Mock
from uuid import uuid4

from common.constant import StatusCode
from registry.constants import ServiceStatus
from registry.consumer.service_event_consumer import ServiceCreatedEventConsumer
from registry.infrastructure.models import Organization, Service, ServiceGroup, ServiceReviewHistory, ServiceState
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository
from registry.testcases.functional_testcases.test_variables import service_metadata


class TestServiceEventConsumer(unittest.TestCase):
    def setUp(self):
        self.org_repo = OrganizationPublisherRepository()
        self.service_repo = ServicePublisherRepository()

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(
        read_bytesio_from_ipfs=Mock(return_value=""),
        read_file_from_ipfs=Mock(return_value=json.loads(json.dumps(service_metadata))),
        write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch("common.boto_utils.BotoUtils.invoke_lambda", return_value={"statusCode": StatusCode.CREATED})
    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.blockchain_util.BlockChainUtil')
    def test_on_service_created_event(self, mock_block_chain_util, mock_s3_push, mock_boto, mock_ipfs):
        org_uuid = str(uuid4())
        service_uuid = str(uuid4())
        self.org_repo.add_item(
            Organization(
                name="test_org",
                org_id="test_org_id",
                uuid=org_uuid,
                org_type="organization",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                addresses=[],
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )
        self.service_repo.add_item(
            Service(
                org_uuid=org_uuid,
                uuid=service_uuid,
                display_name="test_display_name",
                service_id="test_service_id",
                metadata_uri="Qasdfghjklqwertyuiopzxcvbnm",
                short_description="test_short_description",
                description="test_description",
                project_url="https://dummy.io",
                ranking=1,
                tags=["tag1", "tag2"],
                created_on=datetime.utcnow(), updated_on=datetime.utcnow()
            )
        )
        self.service_repo.add_item(
            ServiceState(
                row_id=randrange(10000),
                org_uuid=org_uuid,
                service_uuid=service_uuid,
                state=ServiceStatus.DRAFT.value,
                transaction_hash='0x1234',
                created_by="dummy_user",
                updated_by="dummy_user",
                created_on=datetime.utcnow(), updated_on=datetime.utcnow()
            )
        )
        self.service_repo.add_item(
            ServiceGroup(
                row_id=randrange(1000),
                org_uuid=org_uuid,
                service_uuid=service_uuid,
                group_id="test_group_id",
                endpoints={"https://dummydaemonendpoint.io": {"verfied": True}},
                daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                free_calls=10,
                free_call_signer_address="0xq2s3e4r5t6y7u8i9o0",
                created_on=datetime.utcnow(), updated_on=datetime.utcnow()
            )
        )
        event = {"data": {'row_id': 202, 'block_no': 6325625, 'event': 'ServiceCreated',
                          'json_str': "{'orgId': b'test_org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'test_service_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': '0x12345',
                          'logIndex': '0', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 59, 37),
                          'row_created': datetime(2019, 10, 21, 9, 59, 37)}, "name": "ServiceCreated"}

        mock_s3_push.return_value = "https://test-s3-push"
        service_event_consumer = ServiceCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                             "http://ipfs.singularitynet.io",
                                                             80, self.service_repo, self.org_repo)
        service_event_consumer.on_event(event=event)

        published_service = self.service_repo.get_service_for_given_service_uuid(org_uuid, service_uuid)

        self.assertEqual(["tag1", "tag2"], published_service.tags)
        self.assertEqual(ServiceStatus.DRAFT.value, published_service.service_state.state)
        self.assertEqual(service_metadata["display_name"], published_service.display_name)
        self.assertEqual(service_metadata["service_description"]["description"], published_service.description)
        self.assertEqual(service_metadata["service_description"]["short_description"],
                         published_service.short_description)
        self.assertEqual(service_metadata["service_description"]["url"], published_service.project_url)
        self.assertDictEqual(
            {"encoding": "proto",
             "service_type": "grpc",
             "model_ipfs_hash": "QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf"},
            published_service.proto
        )
        self.assertEqual(service_metadata["mpe_address"], published_service.mpe_address)
        self.assertEqual("ipfs://QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf", published_service.metadata_uri)
        self.assertDictEqual(service_metadata["contributors"][0], published_service.contributors[0])

        group = published_service.groups[0]
        expected_group = service_metadata["groups"][0]

        self.assertEqual(expected_group["daemon_addresses"], group.daemon_address)
        self.assertEqual(expected_group["group_name"], group.group_name)
        self.assertEqual(expected_group["endpoints"], group._get_endpoints())
        self.assertEqual(expected_group["free_calls"], group.free_calls)
        self.assertEqual(expected_group["free_call_signer_address"], group.free_call_signer_address)
        self.assertEqual(expected_group["group_id"], group.group_id)
        self.assertEqual(expected_group["pricing"], group.pricing)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(
        read_bytesio_from_ipfs=Mock(return_value=""),
        read_file_from_ipfs=Mock(return_value=json.loads(json.dumps(service_metadata))),
        write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.blockchain_util.BlockChainUtil')
    def test_on_service_created_event_from_snet_cli(self, mock_block_chain_util, mock_s3_push, mock_ipfs):
        org_uuid = str(uuid4())
        self.org_repo.add_item(
            Organization(
                name="test_org",
                org_id="test_org_id",
                uuid=org_uuid,
                org_type="organization",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                addresses=[],
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )

        event = {"data": {'row_id': 202, 'block_no': 6325625, 'event': 'ServiceCreated',
                          'json_str': "{'orgId': b'test_org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'test_service_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': '0x12345',
                          'logIndex': '0', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 59, 37),
                          'row_created': datetime(2019, 10, 21, 9, 59, 37)}, "name": "ServiceCreated"}
        mock_s3_push.return_value = "https://test-s3-push"
        service_event_consumer = ServiceCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                             "http://ipfs.singularitynet.io",
                                                             80, self.service_repo, self.org_repo)
        service_event_consumer.on_event(event=event)

        org_uuid, published_service = self.service_repo.get_service_for_given_service_id_and_org_id("test_org_id",
                                                                                                    "test_service_id")
        self.assertEqual(["tag1", "tag2"], published_service.tags)
        self.assertEqual(ServiceStatus.PUBLISHED_UNAPPROVED.value, published_service.service_state.state)
        self.assertEqual(service_metadata["display_name"], published_service.display_name)
        self.assertEqual(service_metadata["service_description"]["description"], published_service.description)
        self.assertEqual(service_metadata["service_description"]["short_description"],
                         published_service.short_description)
        self.assertEqual(service_metadata["service_description"]["url"], published_service.project_url)
        self.assertDictEqual(
            {"encoding": "proto",
             "service_type": "grpc",
             "model_ipfs_hash": "QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf"},
            published_service.proto
        )
        self.assertEqual(service_metadata["mpe_address"], published_service.mpe_address)
        self.assertDictEqual(service_metadata["contributors"][0], published_service.contributors[0])

        group = published_service.groups[0]
        expected_group = service_metadata["groups"][0]

        self.assertEqual(expected_group["daemon_addresses"], group.daemon_address)
        self.assertEqual(expected_group["group_name"], group.group_name)
        self.assertEqual(expected_group["endpoints"], group._get_endpoints())
        self.assertEqual(expected_group["free_calls"], group.free_calls)
        self.assertEqual(expected_group["free_call_signer_address"], group.free_call_signer_address)
        self.assertEqual(expected_group["group_id"], group.group_id)
        self.assertEqual(expected_group["pricing"], group.pricing)

    @patch("common.ipfs_util.IPFSUtil", return_value=Mock(
        read_bytesio_from_ipfs=Mock(return_value=""),
        read_file_from_ipfs=Mock(return_value=json.loads(json.dumps(service_metadata))),
        write_file_in_ipfs=Mock(return_value="Q3E12")))
    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.blockchain_util.BlockChainUtil')
    def test_on_gas_price_boosted_service_created_event(self, mock_block_chain_util, mock_s3_push, mock_ipfs):
        org_uuid = str(uuid4())
        self.org_repo.add_item(
            Organization(
                name="test_org",
                org_id="test_org_id",
                uuid=org_uuid,
                org_type="organization",
                description="that is the dummy org for testcases",
                short_description="that is the short description",
                url="https://dummy.url",
                contacts=[],
                assets={},
                duns_no=12345678,
                origin="PUBLISHER_DAPP",
                groups=[],
                addresses=[],
                metadata_ipfs_uri="#dummyhashdummyhash"
            )
        )

        event = {"data": {'row_id': 202, 'block_no': 6325625, 'event': 'ServiceCreated',
                          'json_str': "{'orgId': b'test_org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'test_service_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': None,
                          'logIndex': '0', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 59, 37),
                          'row_created': datetime(2019, 10, 21, 9, 59, 37)}, "name": "ServiceCreated"}

        mock_s3_push.return_value = "https://test-s3-push"
        service_event_consumer = ServiceCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                             "http://ipfs.singularitynet.io",
                                                             80, self.service_repo, self.org_repo)
        service_event_consumer.on_event(event=event)

        org_uuid, published_service = self.service_repo.get_service_for_given_service_id_and_org_id("test_org_id",
                                                                                                    "test_service_id")
        self.assertEqual(["tag1", "tag2"], published_service.tags)
        self.assertEqual(ServiceStatus.PUBLISHED_UNAPPROVED.value, published_service.service_state.state)
        self.assertEqual(service_metadata["display_name"], published_service.display_name)
        self.assertEqual(service_metadata["service_description"]["description"], published_service.description)
        self.assertEqual(service_metadata["service_description"]["short_description"],
                         published_service.short_description)
        self.assertEqual(service_metadata["service_description"]["url"], published_service.project_url)
        self.assertDictEqual(
            {"encoding": "proto",
             "service_type": "grpc",
             "model_ipfs_hash": "QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf"},
            published_service.proto
        )
        self.assertEqual(service_metadata["mpe_address"], published_service.mpe_address)
        self.assertDictEqual(service_metadata["contributors"][0], published_service.contributors[0])

        group = published_service.groups[0]
        expected_group = service_metadata["groups"][0]

        self.assertEqual(expected_group["daemon_addresses"], group.daemon_address)
        self.assertEqual(expected_group["group_name"], group.group_name)
        self.assertEqual(expected_group["endpoints"], group._get_endpoints())
        self.assertEqual(expected_group["free_calls"], group.free_calls)
        self.assertEqual(expected_group["free_call_signer_address"], group.free_call_signer_address)
        self.assertEqual(expected_group["group_id"], group.group_id)
        self.assertEqual(expected_group["pricing"], group.pricing)

    def tearDown(self):
        self.org_repo.session.query(Organization).delete()
        self.org_repo.session.query(Service).delete()
        self.org_repo.session.query(ServiceGroup).delete()
        self.org_repo.session.query(ServiceState).delete()
        self.org_repo.session.query(ServiceReviewHistory).delete()
        self.org_repo.session.commit()
