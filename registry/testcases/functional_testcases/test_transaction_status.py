from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock
from uuid import uuid4

from registry.application.services.org_transaction_status import OrganizationTransactionStatus
from registry.infrastructure.repositories.organization_repository import (
    OrganizationPublisherRepository,
)
from registry.application.services.service_transaction_status import (
    service_repo,
    ServiceTransactionStatus,
)
from registry.constants import (
    OrganizationMemberStatus,
    OrganizationStatus,
    Role,
    ServiceStatus,
)
from registry.infrastructure.models import (
    Organization,
    OrganizationMember,
    Group,
    OrganizationState,
    Service,
    ServiceState,
    OrganizationAddress,
)

org_repo = OrganizationPublisherRepository()


class TestTransactionStatus(TestCase):
    def setUp(self):
        pass

    @patch("common.blockchain_util.BlockChainUtil")
    def test_update_org_transaction_status(self, mock_blockchain_utils):
        mock_blockchain_utils.return_value = Mock(
            get_transaction_receipt_from_blockchain=Mock(return_value=Mock(status=0))
        )
        test_org_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        current_time = datetime.now()
        org_state = OrganizationState(
            org_uuid=test_org_uuid,
            state=OrganizationStatus.PUBLISH_IN_PROGRESS.value,
            transaction_hash="0x123",
            test_transaction_hash="0x456",
            wallet_address="0x987",
            created_by=username,
            created_on=current_time,
            updated_by=username,
            updated_on=current_time,
            reviewed_by="admin",
            reviewed_on=current_time,
        )

        group = Group(
            name="default_group",
            id="group_id",
            org_uuid=test_org_uuid,
            payment_address="0x123",
            payment_config={
                "payment_expiration_threshold": 40320,
                "payment_channel_storage_type": "etcd",
                "payment_channel_storage_client": {
                    "connection_timeout": "5s",
                    "request_timeout": "3s",
                    "endpoints": ["http://127.0.0.1:2379"],
                },
            },
            status="0",
        )

        organization = Organization(
            uuid=test_org_uuid,
            name="test_org",
            org_id=test_org_id,
            org_type="organization",
            origin="PUBLISHER_PORTAL",
            description="this is long description",
            short_description="this is short description",
            url="https://dummy.com",
            duns_no="123456789",
            contacts=[],
            assets={"hero_image": {"url": "some_url", "ipfs_hash": "Q123"}},
            metadata_uri="Q3E12",
            org_state=[org_state],
            groups=[group],
        )
        owner = OrganizationMember(
            invite_code="123",
            org_uuid=test_org_uuid,
            role=Role.OWNER.value,
            username=username,
            status=OrganizationMemberStatus.ACCEPTED.value,
            address="0x123",
            created_on=current_time,
            updated_on=current_time,
            invited_on=current_time,
        )
        org_repo.add_item(organization)
        org_repo.add_item(owner)
        OrganizationTransactionStatus().update_transaction_status()
        org_state = (
            org_repo.session.query(OrganizationState)
            .filter(OrganizationState.org_uuid == test_org_uuid)
            .first()
        )
        if org_state is None:
            assert False
        self.assertEqual(OrganizationStatus.FAILED.value, org_state.state)

    @patch("common.blockchain_util.BlockChainUtil")
    def test_update_service_transaction_status(self, mock_blockchain_utils):
        mock_blockchain_utils.return_value = Mock(
            get_transaction_receipt_from_blockchain=Mock(return_value=Mock(status=0))
        )
        test_org_uuid = uuid4().hex
        test_service_uuid = uuid4().hex
        test_org_id = "org_id"
        username = "karl@cryptonian.io"
        current_time = datetime.now()
        org_state = OrganizationState(
            org_uuid=test_org_uuid,
            state=OrganizationStatus.PUBLISH_IN_PROGRESS.value,
            transaction_hash="0x123",
            test_transaction_hash="0x456",
            wallet_address="0x987",
            created_by=username,
            created_on=current_time,
            updated_by=username,
            updated_on=current_time,
            reviewed_by="admin",
            reviewed_on=current_time,
        )

        group = Group(
            name="default_group",
            id="group_id",
            org_uuid=test_org_uuid,
            payment_address="0x123",
            payment_config={
                "payment_expiration_threshold": 40320,
                "payment_channel_storage_type": "etcd",
                "payment_channel_storage_client": {
                    "connection_timeout": "5s",
                    "request_timeout": "3s",
                    "endpoints": ["http://127.0.0.1:2379"],
                },
            },
            status="0",
        )

        organization = Organization(
            uuid=test_org_uuid,
            name="test_org",
            org_id=test_org_id,
            org_type="organization",
            origin="PUBLISHER_PORTAL",
            description="this is long description",
            short_description="this is short description",
            url="https://dummy.com",
            duns_no="123456789",
            contacts=[],
            assets={"hero_image": {"url": "some_url", "ipfs_hash": "Q123"}},
            metadata_uri="Q3E12",
            org_state=[org_state],
            groups=[group],
        )
        owner = OrganizationMember(
            invite_code="123",
            org_uuid=test_org_uuid,
            role=Role.OWNER.value,
            username=username,
            status=OrganizationMemberStatus.ACCEPTED.value,
            address="0x123",
            created_on=current_time,
            updated_on=current_time,
            invited_on=current_time,
        )
        org_repo.add_item(organization)
        org_repo.add_item(owner)
        service_state = ServiceState(
            org_uuid=test_org_uuid,
            service_uuid=test_service_uuid,
            state=ServiceStatus.PUBLISH_IN_PROGRESS.value,
            created_on=current_time,
            created_by=username,
            updated_by=username,
            updated_on=current_time,
        )
        service = Service(
            org_uuid=test_org_uuid,
            uuid=test_service_uuid,
            display_name="123",
            service_id="test_service",
            created_on=current_time,
            service_state=service_state,
        )
        service_repo.add_item(service)
        ServiceTransactionStatus().update_transaction_status()
        service_state_db = (
            service_repo.session.query(ServiceState)
            .filter(ServiceState.service_uuid == test_service_uuid)
            .first()
        )
        if service_state_db is None:
            assert False
        self.assertEqual(ServiceStatus.FAILED.value, service_state_db.state)

    def tearDown(self):
        org_repo.session.query(OrganizationState).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Organization).delete()
        service_repo.session.query(ServiceState).delete()
        service_repo.session.query(Service).delete()
        org_repo.session.commit()
