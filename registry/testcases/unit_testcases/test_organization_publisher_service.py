import unittest
from datetime import datetime
from uuid import uuid4

from registry.application.services.organization_publisher_service import OrganizationPublisherService, org_repo
from registry.constants import OrganizationStatus, Role
from registry.infrastructure.models import Organization, OrganizationMember, OrganizationState, Group, \
    OrganizationAddress
from registry.domain.models.organization import Organization as DomainOrganization

ORIGIN = "PUBLISHER_DAPP"


class TestOrganizationPublisherService(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_all_org_for_user(self):
        username = "karl@snet.io"
        org_uuid = uuid4().hex
        current_time = datetime.utcnow()
        items = []
        groups = [Group(name="dummy_group", id="group_id", org_uuid=org_uuid, payment_address="0x123", payment_config={
            "payment_expiration_threshold": 40320,
            "payment_channel_storage_type": "etcd",
            "payment_channel_storage_client": {
                "connection_timeout": "5s",
                "request_timeout": "3s",
                "endpoints": [
                    "http://127.0.0.1:2379"
                ]
            }
        })]
        org_state = [OrganizationState(
            org_uuid=org_uuid, state=OrganizationStatus.PUBLISHED.value, transaction_hash="0x123",
            wallet_address="0x123", created_on=current_time, created_by=username,
            updated_by=username, updated_on=current_time,
            reviewed_by="admin_user", reviewed_on=current_time)]

        addresses = [
            OrganizationAddress(org_uuid=org_uuid, address_type="mailing_address", street_address="Street",
                                apartment="appratment", city="city", pincode="560016", state="state", country="country",
                                created_on=current_time, updated_on=current_time)]

        org_repo.add_item(Organization(
            uuid=org_uuid, org_id="org_id",
            name="dummy_org", org_type="Organization", origin=ORIGIN, description="that is the dummy org for testcases",
            short_description="that is the short description", url="dummy.com",
            duns_no="12345678", metadata_ipfs_hash="1234",
            contacts=[{"type": "support", "email": "support_karl@snet.io", "phone": "1234567890"}],
            assets={"hero_image": {"url": "dummy.com", "hash": "Q12R"}},
            org_state=org_state,
            groups=groups, addresses=addresses))

        org_repo.add_item(OrganizationMember(
            invite_code=uuid4().hex, org_uuid=org_uuid, role=Role.OWNER.value, username=username, address="",
            status="PUBLISHED", transaction_hash="", invited_on=current_time,
            created_on=current_time, updated_on=current_time))

        x = 0
        response = OrganizationPublisherService("", username=username).get_all_org_for_user()

    def get_org(self):
        pass

    def tearDown(self):
        org_repo.session.query(Group).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(OrganizationState).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Organization).delete()
        org_repo.session.commit()
