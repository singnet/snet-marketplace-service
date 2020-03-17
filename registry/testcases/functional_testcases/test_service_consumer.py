import unittest
from datetime import datetime
from random import randrange
from unittest.mock import patch
from uuid import uuid4

from registry.constants import ServiceStatus
from registry.consumer.service_event_consumer import ServiceCreatedEventConsumer
from registry.infrastructure.models import Organization, Service, ServiceGroup, ServiceReviewHistory, ServiceState
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        self.org_repo = OrganizationPublisherRepository()
        self.service_repo = ServicePublisherRepository()

    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    @patch('registry.consumer.service_event_consumer.ServiceEventConsumer._fetch_tags')
    def test_on_service_created_event(self, mock_fetch_tags, nock_read_bytesio_from_ipfs, mock_ipfs_read, mock_s3_push):
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
                created_on=datetime.utcnow(), updated_on=datetime.utcnow()
            )
        )
        self.service_repo.add_item(
            ServiceState(
                row_id=randrange(10000),
                org_uuid=org_uuid,
                service_uuid=service_uuid,
                state=ServiceStatus.DRAFT.value,
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
                endpoints=["https://dummydaemonendpoint.io"],
                daemon_address=["0xq2w3e4rr5t6y7u8i9"],
                free_calls=10,
                free_call_signer_address="0xq2s3e4r5t6y7u8i9o0",
                created_on=datetime.utcnow(), updated_on=datetime.utcnow()
            )
        )
        event = {"data": {'row_id': 202, 'block_no': 6325625, 'event': 'ServiceCreated',
                          'json_str': "{'orgId': b'test_org_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'test_service_id\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': 'b"\\xa7P*\\xaf\\xfd\\xd5.E\\x8c\\x0bKAF\'\\x15\\x03\\xef\\xdaO\'\\x86/<\\xfb\\xc4\\xf0@\\xf0\\xc1P\\x8c\\xc7"',
                          'logIndex': '0', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 59, 37),
                          'row_created': datetime(2019, 10, 21, 9, 59, 37)}, "name": "ServiceCreated"}

        nock_read_bytesio_from_ipfs.return_value = "some_value to_be_pushed_to_s3_whic_is_mocked"
        mock_ipfs_read.return_value = {
            "version": 1,
            "display_name": "Annotation Service",
            "encoding": "proto",
            "service_type": "grpc",
            "model_ipfs_hash": "QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf",
            "mpe_address": "0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C",
            "groups": [
                {
                    "group_name": "default_group",
                    "pricing": [
                        {
                            "price_model": "fixed_price",
                            "price_in_cogs": 1,
                            "default": True
                        }
                    ],
                    "endpoints": [
                        "https://mozi.ai:8000"
                    ],
                    "group_id": "m5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc="
                }
            ],
            "assets": {
                "hero_image": "QmVcE6fEDP764ibadXTjZHk251Lmt5xAxdc4P9mPA4kksk/hero_gene-annotation-2b.png"
            },
            "service_description": {
                "url": "https://mozi-ai.github.io/annotation-service/",
                "description": "Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.",
                "short_description": "short description"
            },
            "contributors": [
                {
                    "name": "dummy dummy",
                    "email_id": "dummy@dummy.io"
                }
            ]
        }
        mock_fetch_tags.return_value = ["tag1", "tag2"]
        mock_s3_push.return_value = "https://test-s3-push"
        service_event_consumer = ServiceCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                             "http://ipfs.singularitynet.io",
                                                             80, self.service_repo, self.org_repo)
        service_event_consumer.on_event(event=event)

        published_service = self.service_repo.get_service_for_given_service_uuid(org_uuid, service_uuid)
        assert published_service.display_name == "Annotation Service"
        assert published_service.tags[0] == "tag1"
        assert published_service.groups[0].group_name == "default_group"
        assert published_service.groups[0].pricing[0]['price_model'] == "fixed_price"
        assert published_service.service_state.state == "PUBLISHED"

    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    @patch('registry.consumer.service_event_consumer.ServiceEventConsumer._fetch_tags')
    def test_on_service_created_event_from_snet_cli(self, mock_fetch_tags, nock_read_bytesio_from_ipfs, mock_ipfs_read,
                                                    mock_s3_push):
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
                          'transactionHash': 'b"\\xa7P*\\xaf\\xfd\\xd5.E\\x8c\\x0bKAF\'\\x15\\x03\\xef\\xdaO\'\\x86/<\\xfb\\xc4\\xf0@\\xf0\\xc1P\\x8c\\xc7"',
                          'logIndex': '0', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 59, 37),
                          'row_created': datetime(2019, 10, 21, 9, 59, 37)}, "name": "ServiceCreated"}

        nock_read_bytesio_from_ipfs.return_value = "some_value to_be_pushed_to_s3_whic_is_mocked"
        mock_ipfs_read.return_value = {
            "version": 1,
            "display_name": "Annotation Service",
            "encoding": "proto",
            "service_type": "grpc",
            "model_ipfs_hash": "QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf",
            "mpe_address": "0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C",
            "groups": [
                {
                    "group_name": "default_group",
                    "pricing": [
                        {
                            "price_model": "fixed_price",
                            "price_in_cogs": 1,
                            "default": True
                        }
                    ],
                    "endpoints": [
                        "https://mozi.ai:8000"
                    ],
                    "group_id": "m5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc="
                }
            ],
            "assets": {
                "hero_image": "QmVcE6fEDP764ibadXTjZHk251Lmt5xAxdc4P9mPA4kksk/hero_gene-annotation-2b.png"
            },
            "service_description": {
                "url": "https://mozi-ai.github.io/annotation-service/",
                "description": "Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.",
                "short_description": "short description"
            },
            "contributors": [
                {
                    "name": "dummy dummy",
                    "email_id": "dummy@dummy.io"
                }
            ]
        }
        mock_fetch_tags.return_value = ["tag1", "tag2"]
        mock_s3_push.return_value = "https://test-s3-push"
        service_event_consumer = ServiceCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                             "http://ipfs.singularitynet.io",
                                                             80, self.service_repo, self.org_repo)
        service_event_consumer.on_event(event=event)

        org_uuid, published_service = self.service_repo.get_service_for_given_service_id_and_org_id("test_org_id",
                                                                                                    "test_service_id")
        assert published_service.display_name == "Annotation Service"
        assert published_service.tags[0] == "tag1"
        assert published_service.groups[0].group_name == "default_group"
        assert published_service.groups[0].pricing[0]['price_model'] == "fixed_price"
        assert published_service.service_state.state == "PUBLISHED_UNAPPROVED"

    def tearDown(self):
        self.org_repo.session.query(Organization).delete()
        self.org_repo.session.query(Service).delete()
        self.org_repo.session.query(ServiceGroup).delete()
        self.org_repo.session.query(ServiceState).delete()
        self.org_repo.session.commit()
        self.service_repo.session.query(Service).delete()
        self.service_repo.session.query(ServiceState).delete()
        self.service_repo.session.query(ServiceGroup).delete()
        self.service_repo.session.query(ServiceReviewHistory).delete()
