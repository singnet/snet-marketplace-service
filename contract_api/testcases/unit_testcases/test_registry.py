from unittest import TestCase

from common.repository import Repository
from contract_api.config import NETWORK_ID, NETWORKS
from contract_api.infrastructure.models import ServiceMedia, OffchainServiceConfig as OffchainServiceConfigDB
from contract_api.infrastructure.repositories.service_media_repository import ServiceMediaRepository
from contract_api.infrastructure.repositories.service_repository import OffchainServiceConfigRepository
from contract_api.application.services.registry import Registry
from contract_api.testcases.test_variables import GET_SERVICE_RESPONSE, TEST_ORG_ID, TEST_SERVICE_ID

db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
service_media_repo = ServiceMediaRepository()
offchain_service_repo = OffchainServiceConfigRepository()
modified_date = "2021-08-19 00:01:20"


class TestRegistry(TestCase):
    def test_curation(self):
        registry = Registry(obj_repo=db)
        insert_service_query = f"""INSERT INTO service (org_id,service_id,service_path,hash_uri,is_curated,service_email
        ,row_created,row_updated) VALUES ('{TEST_ORG_ID}','{TEST_SERVICE_ID}',NULL,'QmQtm73kmKhv6mKTkn7qW3uMPtgK6c5Qytb11sCxY98s5j',0,
        NULL,'2019-08-23 07:00:31','2020-03-18 13:07:55');"""
        db.execute(insert_service_query)
        registry.curate_service(TEST_ORG_ID, TEST_SERVICE_ID, True)
        service_details = db.execute("SELECT is_curated FROM service where service_id=%s and org_id=%s",
                                     [TEST_SERVICE_ID, TEST_ORG_ID])
        if len(service_details) > 0:
            assert service_details[0]['is_curated'] == 1
        else:
            assert False

        registry.curate_service(TEST_ORG_ID, TEST_SERVICE_ID, False)
        service_details = db.execute("SELECT is_curated FROM service where service_id=%s and org_id=%s",
                                     [TEST_SERVICE_ID, TEST_ORG_ID])
        if len(service_details) > 0:
            assert service_details[0]['is_curated'] == 0
        else:
            assert False

    def test_get_service_data_by_org_id_and_service_id_with_media(self):
        registry = Registry(obj_repo=db)
        self.tearDown()

        insert_organization_query = f"""INSERT INTO organization
        (row_id ,org_id, organization_name, owner_address, org_metadata_uri, org_email, org_assets_url, row_created, row_updated, description, assets_hash, contacts)
        VALUES(10,'{TEST_ORG_ID}', '{TEST_SERVICE_ID}', """ + """'owner_add', 'uri', 'email', '{"url":"google.com"}', '2021-01-08 05:48:26', '2021-01-08 05:48:26', 'description', '{}','{}');"""
        db.execute(insert_organization_query)

        insert_service_query = f"""INSERT INTO service
        (row_id ,org_id, service_id, service_path, hash_uri, is_curated, service_email, row_created, row_updated)
        VALUES(10,'{TEST_ORG_ID}', '{TEST_SERVICE_ID}', """ + """ 'service_path', 'test_ipfs_hash', 1, 'email', '2021-01-08 05:48:26', '2021-01-08 05:48:26');"""
        db.execute(insert_service_query)

        insert_metadata_query = f"""INSERT INTO service_metadata
        (row_id ,service_row_id, org_id, service_id, display_name, description, short_description,demo_component_available, url, json, model_hash, encoding, `type`, mpe_address, assets_url, assets_hash, service_rating, ranking, contributors, row_created, row_updated)
        VALUES(10,10, '{TEST_ORG_ID}', '{TEST_SERVICE_ID}', """ + """ 'test_display_name', 'test_description', 'short description',0, 'test_url', '{"name":"test_name", "age":31, "city":"test_city"}', 'test_hash', 'proto', 'grpc', 'test_mpe_address','{"hero_image": "https://test-s3-push"}', '{"hero_image": "test_hero_image_hash"}','{"rating": 0.0, "total_users_rated": 0}', 1, '[{"name": "dummy dummy", "email_id": "dummy@dummy.io"}]', '2021-01-08 05:48:26', '2021-01-08 05:48:26')"""
        db.execute(insert_metadata_query)

        service_media_repo.add_item(ServiceMedia(
            row_id=8,
            service_row_id=10,
            org_id=TEST_ORG_ID,
            service_id=TEST_SERVICE_ID,
            url="test_media_s3_url",
            order=0,
            asset_type="grpc-stub",
            file_type="grpc-stub/nodejs",
            alt_text="",
            hash_uri="",
            created_on="2021-06-11 14:21:25",
            updated_on="2021-06-11 14:21:25"
        ))

        service_media_repo.add_item(ServiceMedia(
            row_id=10,
            service_row_id=10,
            org_id=TEST_ORG_ID,
            service_id=TEST_SERVICE_ID,
            url="https://test-s3-push",
            order=5,
            asset_type="hero_image",
            file_type="image",
            alt_text="data is missing",
            hash_uri="Qmbb7tmKZX2TSxDKsK6DEAbp3tPgNUYP11CC93Cft7EkFb",
            created_on="2021-01-08 13:31:50",
            updated_on="2021-01-08 13:31:50"
        ))

        response = registry.get_service(TEST_ORG_ID, TEST_SERVICE_ID)

        result = {}
        result.update(GET_SERVICE_RESPONSE["BASE"])
        result.update(GET_SERVICE_RESPONSE["MEDIA"])
        self.assertDictEqual(response, result)

        offchain_service_repo.add_item(OffchainServiceConfigDB(
            org_id=TEST_ORG_ID,
            service_id=TEST_SERVICE_ID,
            parameter_name="demo_component_url",
            parameter_value="sample_demo_url",
            created_on=modified_date,
            updated_on=modified_date,
        ))
        offchain_service_repo.add_item(OffchainServiceConfigDB(
            org_id=TEST_ORG_ID,
            service_id=TEST_SERVICE_ID,
            parameter_name="demo_component_status",
            parameter_value="PENDING",
            created_on=modified_date,
            updated_on=modified_date,
        ))
        offchain_service_repo.add_item(OffchainServiceConfigDB(
            org_id=TEST_ORG_ID,
            service_id=TEST_SERVICE_ID,
            parameter_name="demo_component_required",
            parameter_value=1,
            created_on=modified_date,
            updated_on=modified_date,
        ))

        response = registry.get_service(TEST_ORG_ID, TEST_SERVICE_ID)

        result = {}
        result.update(GET_SERVICE_RESPONSE["BASE"])
        result.update(GET_SERVICE_RESPONSE["MEDIA"])
        result.update({"demo_component": {'demo_component_url': 'sample_demo_url',
                                          'demo_component_required': 1,
                                          'demo_component_status': 'PENDING',
                                          'demo_component_last_modified': "2021-08-19T00:01:20"
                                          },
                       "demo_component_required": 1
                       })
        self.assertDictEqual(response, result)

    def test_get_service_data_by_org_id_and_service_id_without_media(self):
        registry = Registry(obj_repo=db)
        self.tearDown()

        insert_organization_query = f"""INSERT INTO organization
        (row_id ,org_id, organization_name, owner_address, org_metadata_uri, org_email, org_assets_url, row_created, row_updated, description, assets_hash, contacts)
        VALUES(10, '{TEST_ORG_ID}', '{TEST_SERVICE_ID}', """ + """ 'owner_add', 'uri', 'email', '{"url":"google.com"}', '2021-01-08 05:48:26', '2021-01-08 05:48:26', 'description', '{}','{}');"""
        db.execute(insert_organization_query)

        insert_service_query = f"""INSERT INTO service
        (row_id ,org_id, service_id, service_path, hash_uri, is_curated, service_email, row_created, row_updated)
        VALUES(10,  '{TEST_ORG_ID}', '{TEST_SERVICE_ID}', """ + """'service_path', 'test_ipfs_hash',
         1, 'email', '2021-01-08 05:48:26', '2021-01-08 05:48:26');"""
        db.execute(insert_service_query)

        # intentionally omitted the value for demo_component_available inorder to test the default value
        insert_metadata_query = f"""INSERT INTO service_metadata
        (row_id ,service_row_id, org_id, service_id, display_name, description, short_description, url, json, model_hash, encoding, `type`, mpe_address, assets_url, assets_hash, service_rating, ranking, contributors, row_created, row_updated)
        VALUES(10,10,  '{TEST_ORG_ID}', '{TEST_SERVICE_ID}', """ + """ 'test_display_name', 'test_description', 'short description', 'test_url', '{"name":"test_name", "age":31, "city":"test_city"}', 'test_hash', 'proto', 'grpc', 'test_mpe_address','{"hero_image": "https://test-s3-push"}', '{"hero_image": "test_hero_image_hash"}','{"rating": 0.0, "total_users_rated": 0}', 1, '[{"name": "dummy dummy", "email_id": "dummy@dummy.io"}]', '2021-01-08 05:48:26', '2021-01-08 05:48:26')"""
        db.execute(insert_metadata_query)

        response = registry.get_service(TEST_ORG_ID, TEST_SERVICE_ID)
        self.assertDictEqual(response, GET_SERVICE_RESPONSE["BASE"])

    def tearDown(self):
        db.execute("DELETE FROM service WHERE 1")
        db.execute("DELETE FROM organization WHERE 1")
        db.execute("DELETE FROM service WHERE 1")
        db.execute("DELETE FROM service_metadata WHERE 1")
        service_media_repo.session.query(ServiceMedia).delete()
        offchain_service_repo.session.query(OffchainServiceConfigDB).delete()
        offchain_service_repo.session.commit()
        service_media_repo.session.commit()
