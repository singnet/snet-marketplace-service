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

    def test_get_service_data_by_org_id_and_service_id_with_media(self):
        registry = Registry(obj_repo=db)
        self.clear_dependencies()

        insert_organization_query = """INSERT INTO organization
        (row_id ,org_id, organization_name, owner_address, org_metadata_uri, org_email, org_assets_url, row_created, row_updated, description, assets_hash, contacts)
        VALUES(10,'snet', 'gene-annotation-service', 'owner_add', 'uri', 'email', '{"url":"google.com"}', '2021-01-08 05:48:26', '2021-01-08 05:48:26', 'description', '{}','{}');"""
        db.execute(insert_organization_query)

        insert_service_query = """INSERT INTO service
        (row_id ,org_id, service_id, service_path, ipfs_hash, is_curated, service_email, row_created, row_updated)
        VALUES(10,'snet', 'gene-annotation-service', 'service_path', 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf', 1, 'email', '2021-01-08 05:48:26', '2021-01-08 05:48:26');"""
        db.execute(insert_service_query)

        insert_metadata_query = """INSERT INTO service_metadata
        (row_id ,service_row_id, org_id, service_id, display_name, description, short_description,demo_component_available, url, json, model_ipfs_hash, encoding, `type`, mpe_address, assets_url, assets_hash, service_rating, ranking, contributors, row_created, row_updated)
        VALUES(10,10, 'snet', 'gene-annotation-service', 'Annotation Service', 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.', 'short description',0, 'https://mozi-ai.github.io/annotation-service/', '{"name":"John", "age":31, "city":"New York"}', 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf', 'proto', 'grpc', '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C','{"hero_image": "https://test-s3-push"}', '{"hero_image": "QmVcE6fEDP764ibadXTjZHk251Lmt5xAxdc4P9mPA4kksk/hero_gene-annotation-2b.png"}','{"rating": 0.0, "total_users_rated": 0}', 1, '[{"name": "dummy dummy", "email_id": "dummy@dummy.io"}]', '2021-01-08 05:48:26', '2021-01-08 05:48:26')"""
        db.execute(insert_metadata_query)

        insert_service_media = """INSERT INTO service_media
        (row_id,org_id, service_id, url, `order`, file_type, asset_type, alt_text, created_on, updated_on, ipfs_url, service_row_id)
        VALUES(10,'snet', 'gene-annotation-service', 'https://test-s3-push', 5, 'text', 'hero_image','data is missing', '2021-01-08 13:31:50', '2021-01-08 13:31:50', 'Qmbb7tmKZX2TSxDKsK6DEAbp3tPgNUYP11CC93Cft7EkFb/hero_fbprophet_forecast1', 10);"""
        db.execute(insert_service_media)

        response = registry.get_service_data_by_org_id_and_service_id('snet','gene-annotation-service')

        assert response == {'service_row_id': 10,
                             'org_id': 'snet',
                             'service_id': 'gene-annotation-service',
                             'display_name': 'Annotation Service',
                             'description': 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.',
                             'short_description': 'short description',
                             'demo_component_available': 0,
                             'url': 'https://mozi-ai.github.io/annotation-service/',
                             'json': '{"name":"John", "age":31, "city":"New York"}',
                             'model_ipfs_hash': 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf',
                             'encoding': 'proto', 'type': 'grpc', 'mpe_address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C',
                             'service_rating': {'rating': 0.0, 'total_users_rated': 0},
                             'ranking': 1,
                             'contributors': [{'name': 'dummy dummy', 'email_id': 'dummy@dummy.io'}],
                             'service_path': 'service_path', 'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf',
                             'is_curated': 1,
                             'service_email': 'email',
                             'organization_name': 'gene-annotation-service',
                             'owner_address': 'owner_add',
                             'org_metadata_uri': 'uri',
                             'org_email': 'email',
                             'org_assets_url': {'url': 'google.com'},
                             'org_description': 'description',
                             'contacts': {},
                             'is_available': 0,
                             'groups': [],
                             'tags': [],
                             'media': [{'row_id': 10, 'url': 'https://test-s3-push', 'file_type': 'text', 'order': 5, 'alt_text': 'data is missing',"asset_type":"hero_image"}]
                             }

    def test_get_service_data_by_org_id_and_service_id_without_media(self):
        registry = Registry(obj_repo=db)
        self.clear_dependencies()

        insert_organization_query = """INSERT INTO organization
        (row_id ,org_id, organization_name, owner_address, org_metadata_uri, org_email, org_assets_url, row_created, row_updated, description, assets_hash, contacts)
        VALUES(10,'snet', 'gene-annotation-service', 'owner_add', 'uri', 'email', '{"url":"google.com"}', '2021-01-08 05:48:26', '2021-01-08 05:48:26', 'description', '{}','{}');"""
        db.execute(insert_organization_query)

        insert_service_query = """INSERT INTO service
        (row_id ,org_id, service_id, service_path, ipfs_hash, is_curated, service_email, row_created, row_updated)
        VALUES(10,'snet', 'gene-annotation-service', 'service_path', 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf', 1, 'email', '2021-01-08 05:48:26', '2021-01-08 05:48:26');"""
        db.execute(insert_service_query)

        # intentionally omitted the value for demo_component_available inorder to test the default value
        insert_metadata_query = """INSERT INTO service_metadata
        (row_id ,service_row_id, org_id, service_id, display_name, description, short_description, url, json, model_ipfs_hash, encoding, `type`, mpe_address, assets_url, assets_hash, service_rating, ranking, contributors, row_created, row_updated)
        VALUES(10,10, 'snet', 'gene-annotation-service', 'Annotation Service', 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.', 'short description', 'https://mozi-ai.github.io/annotation-service/', '{"name":"John", "age":31, "city":"New York"}', 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf', 'proto', 'grpc', '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C','{"hero_image": "https://test-s3-push"}', '{"hero_image": "QmVcE6fEDP764ibadXTjZHk251Lmt5xAxdc4P9mPA4kksk/hero_gene-annotation-2b.png"}','{"rating": 0.0, "total_users_rated": 0}', 1, '[{"name": "dummy dummy", "email_id": "dummy@dummy.io"}]', '2021-01-08 05:48:26', '2021-01-08 05:48:26')"""
        db.execute(insert_metadata_query)

        response = registry.get_service_data_by_org_id_and_service_id('snet','gene-annotation-service')

        assert response == {'service_row_id': 10,
                             'org_id': 'snet',
                             'service_id': 'gene-annotation-service',
                             'display_name': 'Annotation Service',
                             'description': 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.',
                             'short_description': 'short description',
                             'demo_component_available':0,
                             'url': 'https://mozi-ai.github.io/annotation-service/',
                             'json': '{"name":"John", "age":31, "city":"New York"}',
                             'model_ipfs_hash': 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf',
                             'encoding': 'proto', 'type': 'grpc', 'mpe_address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C',
                             'service_rating': {'rating': 0.0, 'total_users_rated': 0},
                             'ranking': 1,
                             'contributors': [{'name': 'dummy dummy', 'email_id': 'dummy@dummy.io'}],
                             'service_path': 'service_path', 'ipfs_hash': 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf',
                             'is_curated': 1,
                             'service_email': 'email',
                             'organization_name': 'gene-annotation-service',
                             'owner_address': 'owner_add',
                             'org_metadata_uri': 'uri',
                             'org_email': 'email',
                             'org_assets_url': {'url': 'google.com'},
                             'org_description': 'description',
                             'contacts': {},
                             'is_available': 0,
                             'groups': [],
                             'tags': [],
                             'media': []
                             }

    def clear_dependencies(self):
        db.execute("DELETE FROM service WHERE 1")
        db.execute("DELETE FROM organization WHERE 1")
        db.execute("DELETE FROM service WHERE 1")
        db.execute("DELETE FROM service_metadata WHERE 1")
        db.execute("DELETE FROM service_media WHERE 1")
