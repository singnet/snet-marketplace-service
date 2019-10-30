import unittest
from datetime import datetime

from contract_api.consumers.organization_event_consumer import OrganizationEventConsumer


class TestOrganizationEventConsumer(unittest.TestCase):
    def setUp(self):
        pass


    def test_on_event(self):
        event = {"data": {'row_id': 2, 'block_no': 6243627, 'event': 'OrganizationCreated',
                          'json_str': {'orgId': b'snet\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'},
                          'processed': b'\x00',
                          'transactionHash': "b'y4\\xa4$By/mZ\\x17\\x1d\\xf2\\x18\\xb6aa\\x02\\x1c\\x88P\\x85\\x18w\\x19\\xc9\\x91\\xecX\\xd7E\\x98!'",
                          'logIndex': '1', 'error_code': 1, 'error_msg': '',
                          'row_updated': datetime(2019, 10, 21, 9, 44, 9),
                          'row_created': datetime(2019, 10, 21, 9, 44, 9)}, "name": "OrganizationCreated"}

        org_event_consumer=OrganizationEventConsumer("wss://ropsten.infura.io/ws","http://ipfs.singularitynet.io")
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
