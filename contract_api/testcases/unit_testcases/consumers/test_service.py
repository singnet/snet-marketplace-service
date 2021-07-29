import unittest
from datetime import datetime as dt

from contract_api.infrastructure.repositories.service_repository import ServiceRepository, \
    OffchainServiceConfigRepository

service_repo = ServiceRepository
from contract_api.handlers.service_handlers import service_deployment_status_notification_handler
from contract_api.infrastructure.models import ServiceMetadata, Service

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
                ipfs_hash="hash",
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
            url="",
            json="{}",
            model_ipfs_hash="sample hash",
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

        event = {
            "org_id": "snet",
            "service_id": "gene-annotation-service",
            "build_status": 0
        }
        response = service_deployment_status_notification_handler(event=event, context=None)
        assert response['statusCode'] == 201
        service = service_repo.get_service(org_id="snet", service_id="gene-annotation-service")
        service.is_curated == 0

    def tearDown(self):
        service_repo.session.query(Service).delete()
        service_repo.session.query(ServiceMetadata).delete()
        service_repo.session.commit()