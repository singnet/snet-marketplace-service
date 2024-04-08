import unittest
from datetime import datetime
from unittest.mock import patch

from common.repository import Repository
from contract_api.config import NETWORKS, NETWORK_ID
from contract_api.consumers.organization_event_consumer import OrganizationCreatedEventConsumer
from contract_api.dao.organization_repository import OrganizationRepository


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass

    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')
    @patch(
        'contract_api.consumers.organization_event_consumer.OrganizationEventConsumer._get_org_details_from_blockchain')
    def test_organziation_create_update_event(self, mock_get_org_details_from_blockchain, nock_read_bytesio_from_ipfs,
                                              mock_ipfs_read, mock_s3_push):
        event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
                          'json_str': "{'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
                          'processed': b'\x00',
                          'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
                          'logIndex': '1', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 44, 9),
                          'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}

        nock_read_bytesio_from_ipfs.return_value = ""
        mock_s3_push.return_value = "http://test-s3-push"
        ipfs_mock_value = {
            "org_name": "organization_name",
            "org_id": "org_id1",
            "support": {
                "email_id": "abcd@abcdef.com",
                "phone": "1234567890",
            },
            "contacts": [
                {
                    "contact_type": "support",
                    "email_id": "abcd@abcdef.com",
                    "phone": "1234567890"
                },
                {
                    "contact_type": "dummy",
                    "email_id": "dummy@abcdef.com",
                    "phone": "1234567890"
                }
            ],
            "description": {},
            "assets": {
                "hero_image": "QmNW2jjz11enwbRrF1mJ2LdaQPeZVEtmKU8Uq7kpEkmXCc/hero_gene-annotation.png"
            },
            "groups": [
                {
                    "group_name": "default_group2",
                    "group_id": "99ybRIg2wAx55mqVsA6sB4S7WxPQHNKqa4BPu/bhj+U=",
                    "payment": {
                        "payment_address": "0x671276c61943A35D5F230d076bDFd91B0c47bF09",
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                },
                {
                    "group_name": "default_group2",
                    "group_id": "99ybRIg2wAx55mqVsA6sB6S7WxPQHNKqa4BPu/bhj+U=",
                    "payment": {
                        "payment_address": "0x671276c61943A35D5F230d076bDFd91B0c47bF09",
                        "payment_expiration_threshold": 40320,
                        "payment_channel_storage_type": "etcd",
                        "payment_channel_storage_client": {
                            "connection_timeout": "5s",
                            "request_timeout": "3s",
                            "endpoints": [
                                "http://127.0.0.1:2379"
                            ]
                        }
                    }
                }
            ]
        }
        mock_ipfs_read.return_value = ipfs_mock_value
        mock_get_org_details_from_blockchain.return_value = "snet", ["snet", "", "",
                                                                     "0xB18aac9DE3852F988147287daBD19dF2791C2e0f"], ipfs_mock_value, "abc"
        connection = Repository(NETWORK_ID, NETWORKS=NETWORKS)
        organization_repository = OrganizationRepository(connection)
        organization_repository.delete_organization(org_id='snet')
        organization_repository.delete_organization_groups(org_id='snet')
        org_event_consumer = OrganizationCreatedEventConsumer("wss://ropsten.infura.io/ws",
                                                              "ipfs.singularitynet.io",
                                                              80)
        org_event_consumer.on_event(event=event)

        organization = organization_repository.get_organization(org_id='snet')
        org_group = organization_repository.get_organization_group(org_id='snet')
        assert organization == {'org_id': 'snet', 'organization_name': 'organization_name',
                                'owner_address': '0xB18aac9DE3852F988147287daBD19dF2791C2e0f',
                                'org_metadata_uri': 'abc', 'description': '{}',
                                'org_assets_url': '{"hero_image": "http://test-s3-push"}',
                                'assets_hash': '{"hero_image": "QmNW2jjz11enwbRrF1mJ2LdaQPeZVEtmKU8Uq7kpEkmXCc/hero_gene-annotation.png"}',
                                'contacts': '[{"phone": "1234567890", "email_id": "abcd@abcdef.com", "contact_type": "support"}, {"phone": "1234567890", "email_id": "dummy@abcdef.com", "contact_type": "dummy"}]'}
        assert org_group == [{'org_id': 'snet', 'group_id': '99ybRIg2wAx55mqVsA6sB4S7WxPQHNKqa4BPu/bhj+U=',
                              'group_name': 'default_group2',
                              'payment': '{"payment_address": "0x671276c61943A35D5F230d076bDFd91B0c47bF09", "payment_channel_storage_type": "etcd", "payment_expiration_threshold": 40320, "payment_channel_storage_client": {"endpoints": ["http://127.0.0.1:2379"], "request_timeout": "3s", "connection_timeout": "5s"}}'},
                             {'org_id': 'snet', 'group_id': '99ybRIg2wAx55mqVsA6sB6S7WxPQHNKqa4BPu/bhj+U=',
                              'group_name': 'default_group2',
                              'payment': '{"payment_address": "0x671276c61943A35D5F230d076bDFd91B0c47bF09", "payment_channel_storage_type": "etcd", "payment_expiration_threshold": 40320, "payment_channel_storage_client": {"endpoints": ["http://127.0.0.1:2379"], "request_timeout": "3s", "connection_timeout": "5s"}}'}]
