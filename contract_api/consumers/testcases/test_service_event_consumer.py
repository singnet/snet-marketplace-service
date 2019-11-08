import unittest
from datetime import datetime

from common.repository import Repository
from contract_api.consumers.service_event_consumer import ServiceCreatedEventConsumer
from unittest.mock import patch, Mock
from contract_api.config import NETWORK_ID, NETWORKS

from contract_api.dao.service_repository import ServiceRepository


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass

    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    def test_on_event(self, nock_read_bytesio_from_ipfs, mock_ipfs_read, mock_s3_push):
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
                "description": "Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions."
            }
        }

        mock_s3_push.return_value = "https://test-s3-push"
        org_event_consumer = ServiceCreatedEventConsumer("wss://ropsten.infura.io/ws", "http://ipfs.singularitynet.io", 80)
        org_event_consumer.on_event(event=event)

        service = service_repository.get_service(org_id='snet', service_id='gene-annotation-service')
        service_metadata = service_repository.get_service_metadata(org_id='snet', service_id='gene-annotation-service')
        service_endpoints = service_repository.get_service_endpoints(org_id='snet',
                                                                     service_id='gene-annotation-service')
        service_tags = service_repository.get_service_tags(org_id='snet', service_id='gene-annotation-service')

        print(123)
        assert service == {'org_id': 'snet', 'service_id': 'gene-annotation-service', 'service_path': None,
                           'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf', 'is_curated': 0}
        assert service_metadata == {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                    'display_name': 'Annotation Service',
                                    'description': 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.',
                                    'url': 'https://mozi-ai.github.io/annotation-service/', 'json': '',
                                    'model_ipfs_hash': 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf',
                                    'encoding': 'proto', 'type': 'grpc',
                                    'mpe_address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C',
                                    'assets_url': '{"hero_image": "https://test-s3-push"}',
                                    'assets_hash': '{"hero_image": "QmVcE6fEDP764ibadXTjZHk251Lmt5xAxdc4P9mPA4kksk/hero_gene-annotation-2b.png"}',
                                    'service_rating': '{"rating": 0.0, "total_users_rated": 0}', 'ranking': 1,
                                    'contributors': None}
        assert service_endpoints == [{'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                      'group_id': 'm5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc=',
                                      'endpoint': 'https://mozi.ai:8000'}]
        assert service_tags == [{'org_id': 'snet', 'service_id': 'gene-annotation-service', 'tag_name': 'atomese'},
                                {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                 'tag_name': 'bioinformatics'},
                                {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                 'tag_name': 'gene-ontology'},
                                {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                 'tag_name': 'human-gene-annotation'},
                                {'org_id': 'snet', 'service_id': 'gene-annotation-service', 'tag_name': 'reactome'}]


if __name__ == "__main__":
    unittest.main()

    # event ={"data": {'row_id': 536, 'block_no': 6247992, 'event': 'ServiceCreated', 'json_str': "{'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'freecall\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmQtm73kmKhv6mKTkn7qW3uMPtgK6c5Qytb11sCxY98s5j\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}", 'processed': 0, 'transactionHash': "b'~\\xb5\\x0c\\x93\\xe7y\\xc1\\x9d\\xf2I\\xef3\\xc6H\\x16\\xbd\\xab \\xa4\\xb5\\r\\xaau5eb\\x82B\\xe0\\x1c\\xf7\\xdd'", 'logIndex': '43', 'error_code': 0, 'error_msg': '', 'row_updated': '2019-11-07 07:17:06', 'row_created': '2019-11-07 07:17:06'},"name":"ServiceCreated"}
    # org_event_consumer = ServiceEventConsumer("wss://ropsten.infura.io/ws", "http://ipfs.singularitynet.io", 80)
    # try:
    #     org_event_consumer.on_event(event=event)
    # except Exception as e:
    #     print(e)
    #     raise e
