from unittest import TestCase

from common.repository import Repository
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.registry import Registry

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)


class TestServiceHandler(TestCase):
    def clear_dependencies(self):
        db.execute("DELETE FROM service WHERE 1")
        db.execute("DELETE FROM organization WHERE 1")
        db.execute("DELETE FROM service WHERE 1")
        db.execute("DELETE FROM service_metadata WHERE 1")
        db.execute("DELETE FROM service_media WHERE 1")
        db.execute("DELETE FROM service_endpoint WHERE 1")

    def test_get_service_post(self):
        assert True
        # registry = Registry(obj_repo=db)
        #
        # self.clear_dependencies()
        #
        # insert_organization_query = """INSERT INTO organization
        #        (row_id ,org_id, organization_name, owner_address, org_metadata_uri, org_email, org_assets_url, row_created, row_updated, description, assets_hash, contacts)
        #        VALUES(10,'snet', 'gene-annotation-service', 'owner_add', 'uri', 'email', '{"url":"google.com"}', '2021-01-08 05:48:26', '2021-01-08 05:48:26', 'description', '{}','{}');"""
        # db.execute(insert_organization_query)
        #
        # insert_service_query = """INSERT INTO service
        #        (row_id ,org_id, service_id, service_path, hash_uri, is_curated, service_email, row_created, row_updated)
        #        VALUES(10,'snet', 'gene-annotation-service', 'service_path', 'QmdGjaVYPMSGpC1qT3LDALSNCCu7JPf7j51H1GQirvQJYf', 1, 'email', '2021-01-08 05:48:26', '2021-01-08 05:48:26');"""
        # db.execute(insert_service_query)
        #
        # insert_metadata_query = """INSERT INTO service_metadata
        #        (row_id ,service_row_id, org_id, service_id, display_name, description, short_description, url, json, model_hash, encoding, `type`, mpe_address, assets_url, assets_hash, service_rating, ranking, contributors, row_created, row_updated)
        #        VALUES(10,10, 'snet', 'gene-annotation-service', 'Annotation Service', 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.', 'short description', 'https://mozi-ai.github.io/annotation-service/', '{"name":"John", "age":31, "city":"New York"}', 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf', 'proto', 'grpc', '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C','{"hero_image": "https://test-s3-push"}', '{"hero_image": "QmVcE6fEDP764ibadXTjZHk251Lmt5xAxdc4P9mPA4kksk/hero_gene-annotation-2b.png"}','{"rating": 0.0, "total_users_rated": 0}', 1, '[{"name": "dummy dummy", "email_id": "dummy@dummy.io"}]', '2021-01-08 05:48:26', '2021-01-08 05:48:26')"""
        # db.execute(insert_metadata_query)
        #
        # insert_service_media = """INSERT INTO service_media
        #       (row_id,org_id, service_id, url, `order`, file_type, asset_type, alt_text, created_on, updated_on, hash_uri, service_row_id)
        #       VALUES(10,'snet', 'gene-annotation-service', 'https://test-s3-push', 5, 'text', 'hero_image','data is missing', '2021-01-08 13:31:50', '2021-01-08 13:31:50', 'Qmbb7tmKZX2TSxDKsK6DEAbp3tPgNUYP11CC93Cft7EkFb/hero_fbprophet_forecast1', 10);"""
        # db.execute(insert_service_media)
        #
        # insert_service_endpoint = """INSERT INTO service_endpoint
        # (service_row_id, org_id, service_id, group_id, endpoint, is_available, last_check_timestamp, next_check_timestamp, failed_status_count, row_created, row_updated)
        # VALUES(10, 'snet', 'gene-annotation-service', 'm5FKWq4hW0foGW5qSbzGSjgZRuKs7A1ZwbIrJ9e96rc=','https://mozi.ai:8000',1, '2020-05-21 06:53:30', '2020-05-21 06:53:30', 1, '2020-05-21 06:53:30', '2020-05-21 06:53:30');"""
        # db.execute(insert_service_endpoint)
        #
        # body = {"q": "", "limit": 12, "offset": 0, "total_count": 0, "s": "all", "sort_by": "ranking", "order_by": "asc","filters": []}
        # response = registry.get_all_srvcs(qry_param=body)
        # assert response == {'total_count': 1, 'offset': 0, 'limit': 12, 'result': [{'service_row_id': 10, 'org_id': 'snet', 'service_id': 'gene-annotation-service', 'display_name': 'Annotation Service', 'description': 'Use this service to annotate a humane genome with uniform terms, Reactome pathway memberships, and BioGrid protein interactions.', 'short_description': 'short description', 'url': 'https://mozi-ai.github.io/annotation-service/', 'json': '{"name":"John", "age":31, "city":"New York"}', 'model_ipfs_hash': 'QmXqonxB9EvNBe11J8oCYXMQAtPKAb2x8CyFLmQpkvVaLf', 'encoding': 'proto', 'type': 'grpc', 'mpe_address': '0x8FB1dC8df86b388C7e00689d1eCb533A160B4D0C', 'service_rating': {'rating': 0.0, 'total_users_rated': 0}, 'ranking': 1, 'contributors': [{'name': 'dummy dummy', 'email_id': 'dummy@dummy.io'}], 'organization_name': 'gene-annotation-service', 'org_assets_url': {'url': 'google.com'}, 'contacts': [], 'tags': [], 'is_available': 1, 'media': {'org_id': 'snet', 'service_id': 'gene-annotation-service', 'file_type': 'text', 'asset_type': 'hero_image', 'url': 'https://test-s3-push', 'alt_text': 'data is missing', 'order': 5, 'row_id': 10}}]}