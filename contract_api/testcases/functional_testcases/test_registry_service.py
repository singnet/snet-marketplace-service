import json
from unittest import TestCase

from contract_api.application.handler.service_handler import save_offchain_attribute
from contract_api.infrastructure.models import OffchainServiceConfig
from contract_api.infrastructure.repositories.service_repository import ServiceRepository

service_repository = ServiceRepository()


class TestRegistryService(TestCase):
    def setUp(self):
        pass

    def test_save_offchain_attribute(self):
        self.tearDown()
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 0})
        }
        response = save_offchain_attribute(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])["data"]
        assert (response_body["attributes"]["demo_component_required"] == 0)
        event = {
            "pathParameters": {
                "orgId": "test_org_id",
                "serviceId": "test_service_id"
            },
            "body": json.dumps({"demo_component_required": 1})
        }
        response = save_offchain_attribute(event=event, context=None)
        response_body = json.loads(response["body"])["data"]
        assert (response_body["attributes"]["demo_component_required"] == 1)

    def tearDown(self):
        service_repository.session.query(OffchainServiceConfig).delete()
        service_repository.session.commit()
