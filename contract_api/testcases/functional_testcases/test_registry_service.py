import json
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
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component": {
                "demo_component_required": 1,
                "demo_component_url": "new_demo_component_url"
            }})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        del values['attributes']['demo_component_last_modified']
        assert values == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes':
                {
                    'demo_component_required': 1,
                    'demo_component_status': '',
                    'demo_component_url': 'new_demo_component_url',
                }
        }

        mock_publish_demo_files.return_value = "published_url"
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component": {
                "demo_component_required": 0,
                "change_in_demo_component": 1,
                "demo_component_url": "new_demo_component_url"
            }})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        del values['attributes']['demo_component_last_modified']
        assert values == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes':
                {
                    'demo_component_required': 0,
                    'demo_component_status': '',
                    'demo_component_url': 'new_demo_component_url'
                }
        }

        mock_publish_demo_files.return_value = "published_url"
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component": {
                "demo_component_required": 1,
                "change_in_demo_component": 1,
                "demo_component_url": "new_demo_component_url"
            }})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        del values['attributes']['demo_component_last_modified']
        assert values == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes':
                {
                    'demo_component_required': 1,
                    'demo_component_status': 'PENDING',
                    'demo_component_url': 'published_url'
                }
        }

        # no change in existing
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        del values['attributes']['demo_component_last_modified']
        assert values == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes': {
                'demo_component_required': 1,
                'demo_component_status': 'PENDING',
                'demo_component_url': 'published_url'}
        }

        # blank values
        self.tearDown()
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        offchain_values = offchain_repo.get_offchain_service_config("test_org_id", "test_service_id")
        values = offchain_values.to_dict()
        assert values == {
            'org_id': 'test_org_id',
            'service_id': 'test_service_id',
            'attributes': {}
        }

    def tearDown(self):
        service_repository.session.query(OffchainServiceConfig).delete()
        service_repository.session.commit()
