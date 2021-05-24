import unittest
from datetime import datetime
from unittest.mock import patch

from common.repository import Repository
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.consumers.service_event_consumer import ServiceCreatedEventConsumer
from contract_api.dao.service_repository import ServiceRepository


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass

    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    def test_on_service_created_event_with_media(self, nock_read_bytesio_from_ipfs, mock_ipfs_read,
                                                 mock_s3_push):
        event = {"data": {'row_id': 202, 'block_no': 6325625, 'event': 'ServiceCreated',
                          'json_str': "{'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'gene-annotation-service\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': 'b"\\xa7P*\\xaf\\xfd\\xd5.E\\x8c\\x0bKAF\'\\x15\\x03\\xef\\xdaO\'\\x86/<\\xfb\\xc4\\xf0@\\xf0\\xc1P\\x8c\\xc7"',
                          'logIndex': '0', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 59, 37),
                          'row_created': datetime(2019, 10, 21, 9, 59, 37)}, "name": "ServiceCreated"}

        connection = Repository(NETWORK_ID, NETWORKS=NETWORKS)
        service_repository = ServiceRepository(connection)
        service_repository.delete_service(org_id='snet', service_id='gene-annotation-service')
        service_repository.delete_service_dependents(org_id='snet', service_id='gene-annotation-service')

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
                    "free_calls": 12,
                    "free_call_signer_address": "0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F",
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
            "media": [
                {
                    "file_type": "video",
                    "url": "https://youtu.be/7mj-p1Os6QA",
                    "asset_type": "image updated",
                    "order": 5,
                    "alt_text": "alternate text sample updated",
                },
                {
                    "file_type": "text",
                    "url": "Qmbb7tmKZX2TSxDKsK6DEAbp3tPgNUYP11CC93Cft7EkFb/hero_fbprophet_forecast1",
                    "order": 2,
                    "alt_text": "text sample updated",
                }],
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
            ],
            "tags": ["1234", "3241"]
        }
        mock_s3_push.return_value = "https://test-s3-push"
        org_event_consumer = ServiceCreatedEventConsumer("wss://ropsten.infura.io/ws", "http://ipfs.singularitynet.io",
                                                         80)
        org_event_consumer.on_event(event=event)

        service = service_repository.get_service(org_id='snet', service_id='gene-annotation-service')
        service_metadata = service_repository.get_service_metadata(org_id='snet', service_id='gene-annotation-service')
        service_endpoints = service_repository.get_service_endpoints(org_id='snet',
                                                                     service_id='gene-annotation-service')
        service_tags = service_repository.get_service_tags(org_id='snet', service_id='gene-annotation-service')

        service_groups = service_repository.get_service_group(org_id='snet', service_id='gene-annotation-service')

        service_media = service_repository.get_service_media(org_id='snet', service_id='gene-annotation-service')

        assert service == {'org_id': 'snet', 'service_id': 'gene-annotation-service', 'service_path': None,
                           'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf', 'is_curated': 0}
        assert service_metadata == {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                    'display_name': 'Annotation Service',
                                    'description': 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.',
                                    'short_description': 'short description',
                                    'url': 'https://mozi-ai.github.io/annotation-service/', 'json': '',
                                    'model_ipfs_hash': 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf',
                                    'encoding': 'proto', 'type': 'grpc',
                                    'mpe_address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C',
                                    'assets_url': '{}',
                                    'assets_hash': '{}',
                                    'service_rating': '{"rating": 0.0, "total_users_rated": 0}', 'ranking': 1,
                                    'contributors': '[{"name": "dummy dummy", "email_id": "dummy@dummy.io"}]'}
        assert service_endpoints == [{'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                      'group_id': 'm5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc=',
                                      'endpoint': 'https://mozi.ai:8000'}]
        assert service_tags == [{'org_id': 'snet', 'service_id': 'gene-annotation-service', 'tag_name': '1234'},
                                {'org_id': 'snet', 'service_id': 'gene-annotation-service', 'tag_name': '3241'}]

        assert service_groups == {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                  'group_id': 'm5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc=',
                                  'group_name': 'default_group',
                                  'pricing': '[{"default": true, "price_model": "fixed_price", "price_in_cogs": 1}]',
                                  'free_call_signer_address': '0x7DF35C98f41F3Af0df1dc4c7F7D4C19a71Dd059F',
                                  'free_calls': 12}

        for media_item in service_media:
            media_item.pop('row_id')

        assert service_media == [
            {'org_id': 'snet', 'service_id': 'gene-annotation-service', 'url': 'https://youtu.be/7mj-p1Os6QA',
             'order': 5, 'file_type': 'video', 'asset_type': 'image updated',
             'alt_text': 'alternate text sample updated', 'ipfs_url': ''}
        ]
