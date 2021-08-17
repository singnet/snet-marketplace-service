import json
from datetime import datetime as dt
from unittest import TestCase
from unittest.mock import patch

from contract_api.application.handler.service_handler import save_offchain_attribute
from contract_api.infrastructure.models import OffchainServiceConfig
from contract_api.infrastructure.repositories.service_repository import ServiceRepository, \
    OffchainServiceConfigRepository

service_repository = ServiceRepository()
offchain_repo = OffchainServiceConfigRepository()


class TestRegistryService(TestCase):
    def setUp(self):
        pass

    @patch("contract_api.application.service.registry_service.RegistryService.publish_demo_component")
    def test_save_offchain_attribute(self, mock_publish_demo_files):
        self.tearDown()
        mock_publish_demo_files.return_value = "sample_url"
        # New record -> demo_required -> 1
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 1, "demo_component_url": "new_demo_component_url"})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        assert values["attributes"]["demo_component_required"] == 1
        assert values["attributes"]["demo_component_status"] == "PENDING"
        assert values["attributes"]["demo_component_url"] == "sample_url"
        assert True if values["attributes"].get("demo_component_last_modified", None) else False

        # New record -> demo_required -> 0
        self.tearDown()
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 0, "demo_component_url": "new_demo_component_url"})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        assert values == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes': {
                'demo_component_last_modified': None,
                'demo_component_required': 0,
                'demo_component_status': None,
                'demo_component_url': None}
        }

        self.tearDown()
        offchain_repo.add_item(OffchainServiceConfig(
            org_id='test_org_id',
            service_id='test_service_id',
            parameter_name="demo_component_required",
            parameter_value=0,
            created_on=dt.utcnow(),
            updated_on=dt.utcnow()
        ))
        offchain_repo.add_item(OffchainServiceConfig(
            org_id='test_org_id',
            service_id='test_service_id',
            parameter_name="demo_component_url",
            parameter_value="existing_url",
            created_on=dt.utcnow(),
            updated_on=dt.utcnow()
        ))

        # existing record -> demo_required -> 0
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 0, "demo_component_url": "new_demo_component_url"})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        assert values == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes': {
                'demo_component_last_modified': None,
                'demo_component_required': 0,
                'demo_component_status': '',
                'demo_component_url': 'existing_url'
            }
        }

        # existing record -> demo_required -> 1
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 1, "demo_component_url": "new_demo_component_url"})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        assert values["attributes"]["demo_component_required"] == 1
        assert values["attributes"]["demo_component_status"] == "PENDING"
        assert values["attributes"]["demo_component_url"] == "sample_url"
        assert True if values["attributes"].get("demo_component_last_modified", None) else False

    def tearDown(self):
        service_repository.session.query(OffchainServiceConfig).delete()
        service_repository.session.commit()
