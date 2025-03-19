import unittest
from datetime import datetime as dt

from contract_api.infrastructure.repositories.service_repository import ServiceRepository, \
    OffchainServiceConfigRepository

from contract_api.handlers.service_handlers import service_deployment_status_notification_handler
from contract_api.infrastructure.models import ServiceMetadata, Service, OffchainServiceConfig

service_repo = ServiceRepository()
offchain_service_repo = OffchainServiceConfigRepository()


class TestService(unittest.TestCase):
    def setUp(self):
        self.tearDown()
        service_repo.add_item(
            Service(
                row_id=100,
                org_id="snet",
                service_id="gene-annotation-service",
                service_path="",
                hash_uri="hash",
                is_curated=1,
                service_email="service@email.com",
                row_updated=dt.utcnow(),
                row_created=dt.utcnow()
            )
        )
        service_repo.add_item(ServiceMetadata(
            service_row_id=100,
            org_id="snet",
            service_id="gene-annotation_service",
            display_name="annotation_service",
            description="sample description",
            short_description="short description",
            demo_component_available=0,
            url="",
            json="{}",
            model_hash="sample hash",
            encoding="proto",
            type="type",
            mpe_address="sample mpe",
            assets_url={},
            assets_hash={},
            service_rating={},
            ranking=1,
            contributors=[{"name": "dummy dummy", "email_id": "dummy@dummy.io"}],
            row_created=dt.utcnow(),
            row_updated=dt.utcnow(),
        ))

    def test_update_service_demo_component_status(self):
        event = {
            "org_id": "snet",
            "service_id": "gene-annotation-service",
            "build_status": 1
        }
        response = service_deployment_status_notification_handler(event=event, context=None)
        assert response['statusCode'] == 201
        service = service_repo.get_service(org_id="snet", service_id="gene-annotation-service")
        assert service.is_curated == 1
        offchain_response = offchain_service_repo.get_offchain_service_config(org_id="snet",
                                                                              service_id="gene-annotation-service")
        assert offchain_response.to_dict() == {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                     'attributes': {'demo_component_status': 'SUCCESS'}}

        event = {
            "org_id": "snet",
            "service_id": "gene-annotation-service",
            "build_status": 0
        }
        response = service_deployment_status_notification_handler(event=event, context=None)
        assert response['statusCode'] == 201
        service = service_repo.get_service(org_id="snet", service_id="gene-annotation-service")
        assert service.is_curated == 0
        offchain_response = offchain_service_repo.get_offchain_service_config(org_id="snet",
                                                                              service_id="gene-annotation-service")
        assert offchain_response.to_dict() == {'org_id': 'snet', 'service_id': 'gene-annotation-service',
                                     'attributes': {'demo_component_status': 'FAILED'}}

    def tearDown(self):
        offchain_service_repo.session.query(OffchainServiceConfig).delete()
        service_repo.session.query(Service).delete()
        service_repo.session.query(ServiceMetadata).delete()
        service_repo.session.commit()
