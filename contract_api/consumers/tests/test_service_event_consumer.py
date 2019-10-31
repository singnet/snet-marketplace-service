import unittest
from datetime import datetime

from contract_api.consumers.service_event_consumer import ServiceEventConsumer


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass






    def test_on_event(self):
        event={"data":{'row_id': 202, 'block_no': 6325625, 'event': 'ServiceCreated',
         'json_str': "{'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'gene-annotation-service\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
         'processed': b'\x00',
         'transactionHash': 'b"\\xa7P*\\xaf\\xfd\\xd5.E\\x8c\\x0bKAF\'\\x15\\x03\\xef\\xdaO\'\\x86/<\\xfb\\xc4\\xf0@\\xf0\\xc1P\\x8c\\xc7"',
         'logIndex': '0', 'error_code': 1, 'error_msg': '', 'row_updated': datetime(2019, 10, 21, 9, 59, 37),
         'row_created': datetime(2019, 10, 21, 9, 59, 37)},"name":"ServiceCreated"}



        org_event_consumer=ServiceEventConsumer("wss://ropsten.infura.io/ws","http://ipfs.singularitynet.io")
        org_event_consumer.on_event(event=event)


    # def test_on_event(self):
    #
    #     event={"data":{'row_id': 59, 'block_no': 6383816, 'event': 'ServiceMetadataModified',
    #                 'json_str': "{'orgId': b'nginx_snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'nginx_snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'metadataURI': b'ipfs://QmQtm73kmKhv6mKTkn7qW3uMPtgK6c5Qytb11sCxY98s5j\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
    #                 'processed': b'\x00',
    #                 'transactionHash': "b'\\xbf\\x06\\xa5\\xbf0D\\xc1g\\xf2\\xf1\\xfaW\\xcek\\xf0\\xa5\\xf6>\\xd4\\xbe\\x06[\\x85z\\xce~\\xcen\\xeb\\xcd\\x0c,'",
    #                 'logIndex': '6', 'error_code': 1, 'error_msg': '',
    #                 'row_updated': datetime(2019, 10, 21, 9, 44, 10),
    #                 'row_created': datetime(2019, 10, 21, 9, 44, 10)},"name":"ServiceMetadataModified"}
    #
    #
    #
    #     org_event_consumer=ServiceEventConsumer("wss://ropsten.infura.io/ws","http://ipfs.singularitynet.io")
    #     org_event_consumer.on_event(event=event)

    # def test_on_event(self):
    #     event={"data":{'row_id': 86, 'block_no': 6558936, 'event': 'ServiceDeleted',
    #                     'json_str': "{'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00', 'serviceId': b'gene-annotation-service\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'}",
    #                     'processed': b'\x00',
    #                     'transactionHash': "b'\\xdf\\x8f\\x14\\x0c6\\xcb\\xdf\\\\\\x82\\x9f\\\\\\x9f\\xa7ASl\\x1bM\\xc6\\xb8\\xde\\x92\\xbb\\x9f\\x88\\x83v\\xda\\xe11;z'",
    #                     'logIndex': '0', 'error_code': 1, 'error_msg': '',
    #                     'row_updated': datetime(2019, 10, 21, 9, 44, 10),
    #                     'row_created': datetime(2019, 10, 21, 9, 44, 10)},"name":"ServiceDeleted"}
    #
    #     org_event_consumer = ServiceEventConsumer("wss://ropsten.infura.io/ws", "http://ipfs.singularitynet.io")
    #     org_event_consumer.on_event(event=event)
    #
    #






if __name__ == "__main__":
    unittest.main()
