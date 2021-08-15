import json
from unittest import TestCase
from unittest.mock import patch
from contract_api.application.handler.service_handler import save_offchain_attribute
from contract_api.config import ASSETS_COMPONENT_BUCKET_NAME
from contract_api.infrastructure.models import OffchainServiceConfig
from contract_api.infrastructure.repositories.service_repository import ServiceRepository, \
    OffchainServiceConfigRepository

service_repository = ServiceRepository()
offchain_repo = OffchainServiceConfigRepository()


class TestRegistryService(TestCase):
    def setUp(self):
        pass

    @patch("common.boto_utils.BotoUtils.s3_upload_file")
    @patch("common.utils.Utils.extract_zip_and_and_tar")
    def test_save_offchain_attribute(self, mock_prepare_tar, mock_s3_upload):
        self.tearDown()
        mock_prepare_tar.return_value = "tar_file_path"
        mock_s3_upload.return_value = "s3_url"
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 0})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        assert offchain_values.to_dict() == {'org_id': 'test_org_id', 'service_id': 'test_service_id', 'attributes': {'demo_component_required': 0}}

        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 1})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        assert offchain_values.to_dict() == {'org_id': 'test_org_id', 'service_id': 'test_service_id',
                                   'attributes': {'demo_component_required': 1}}

        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({
                "demo_component_required": 1,
                "demo_component_url": "sample_url"
            })
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        assert offchain_values.to_dict() == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes': {
                'demo_component_required': 1,
                'demo_component_status': 'PENDING',
                'demo_component_url': f'https://{ASSETS_COMPONENT_BUCKET_NAME}.s3.amazonaws.com/assets/test_org_id/test_service_id/component.tar.gz'
            }}

    def tearDown(self):
        service_repository.session.query(OffchainServiceConfig).delete()
        service_repository.session.commit()
