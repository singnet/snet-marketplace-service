import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from contract_api.consumers.organization_event_consumer import OrganizationEventConsumer


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass

    @patch('common.s3_util.S3Util.push_io_bytes_to_s3')
    @patch('common.ipfs_util.IPFSUtil.read_file_from_ipfs')
    @patch('common.ipfs_util.IPFSUtil.read_bytesio_from_ipfs')


    def test_on_organziation_create_event(self, nock_read_bytesio_from_ipfs,mock_ipfs_read, mock_s3_push):
        event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
                          'json_str': {'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'},
                          'processed': b'\x00',
                          'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
                          'logIndex': '1', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 44, 9),
                          'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}

        nock_read_bytesio_from_ipfs.return_value= ""
        mock_s3_push.return_value= "http://test-s3-push"
        mock_ipfs_read.return_value = {
            "org_name": "organization_name",
            "org_id": "org_id1",
            "support": {
                "email_id": "abcd@abcdef.com",
                "phone": "1234567890",
            },
            "description": "We do this and that ... Describe your organization here ",
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
                }
            ]
        }
        org_event_consumer=OrganizationEventConsumer("wss://ropsten.infura.io/ws","http://ipfs.singularitynet.io",80)
        org_event_consumer.on_event(event=event)

        blockchain_vents = org_event_consumer.organization_repository.read_registry_events()
        print(123)


    # def test_on_event(self):
    #     event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
    #                       'json_str': {'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'},
    #                       'processed': b'\x00',
    #                       'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
    #                       'logIndex': '1', 'error_code': 1, 'error_msg': '',
    #                       'row_updated': datetime(2019, 10, 21, 9, 44, 9),
    #                       'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}
    #
    #     org_event_consumer=OrganizationEventConsumer("wss://ropsten.infura.io/ws","http://ipfs.singularitynet.io")
    #     org_event_consumer.on_event(event=event)


    # def test_on_event(self):
    #     event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationDeleted',
    #                       'json_str': {'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'},
    #                       'processed': b'\x00',
    #                       'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
    #                       'logIndex': '1', 'error_code': 1, 'error_msg': '',
    #                       'row_updated': datetime(2019, 10, 21, 9, 44, 9),
    #                       'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationDeleted"}
    #
    #     org_event_consumer=OrganizationEventConsumer("wss://ropsten.infura.io/ws","http://ipfs.singularitynet.io")
    #     blockchain_vents=org_event_consumer.organization_dao.read_registry_events()
    #     org_event_consumer.on_event(event=event)








if __name__ == "__main__":
    unittest.main()
