from unittest import TestCase

from common.repository import Repository
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.registry import Registry

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)


class TestRegistry(TestCase):
    def test_curation(self):
        registry = Registry(obj_repo=db)
        insert_service_query = """INSERT INTO service (org_id,service_id,service_path,ipfs_hash,is_curated,service_email
        ,row_created,row_updated) VALUES ('snet','freecall',NULL,'QmQtm73kmKhv6mKTkn7qW3uMPtgK6c5Qytb11sCxY98s5j',0,
        NULL,'2019-08-23 07:00:31','2020-03-18 13:07:55');"""
        db.execute(insert_service_query)
        registry.curate_service('snet', 'freecall', True)
        service_details = db.execute("SELECT is_curated FROM service where service_id=%s and org_id=%s",
                                     ['freecall', 'snet'])
        if len(service_details) > 0:
            assert service_details[0]['is_curated'] == 1
        else:
            assert False

        registry.curate_service('snet', 'freecall', False)
        service_details = db.execute("SELECT is_curated FROM service where service_id=%s and org_id=%s",
                                     ['freecall', 'snet'])
        if len(service_details) > 0:
            assert service_details[0]['is_curated'] == 0
        else:
            assert False

    def tearDown(self):
        db.execute("DELETE FROM service WHERE 1")
