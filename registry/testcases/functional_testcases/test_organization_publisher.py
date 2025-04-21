import json
from unittest import TestCase
from uuid import uuid4

from registry.application.handlers.organization_handlers import (
    save_transaction_hash_for_publish_org,
)
from registry.application.services.organization_publisher_service import org_repo
from registry.constants import OrganizationStatus, Role
from registry.domain.models.organization import Organization as DomainOrganization
from registry.infrastructure.models import (
    OrganizationAddress,
    OrganizationState,
    OrganizationMember,
    Group,
    Organization,
)
from registry.testcases.test_variables import ORG_CONTACTS

ORIGIN = "PUBLISHER"


class TestOrganizationPublisher(TestCase):
    def test_store_transaction_hash(self):
        test_org_uuid = uuid4().hex
        username = "karl@dummy.io"
        wallet_address = "0x321"
        transaction_hash = "0x123"
        nonce = 12
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid,
                "org_id",
                "org_dummy",
                "ORGANIZATION",
                ORIGIN,
                "description",
                "short_description",
                "https://test.io",
                ORG_CONTACTS,
                {},
                "ipfs_hash",
                "123456879",
                [],
                [],
                [],
                [],
            ),
            username,
            OrganizationStatus.PUBLISHED.value,
        )
        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "pathParameters": {"org_uuid": test_org_uuid},
            "body": json.dumps(
                {
                    "transaction_hash": transaction_hash,
                    "wallet_address": wallet_address,
                    "nonce": nonce,
                }
            ),
        }
        save_transaction_hash_for_publish_org(event, None)
        organization = (
            org_repo.session.query(Organization).filter(Organization.uuid == test_org_uuid).first()
        )
        owner = (
            org_repo.session.query(OrganizationMember)
            .filter(OrganizationMember.org_uuid == test_org_uuid)
            .filter(OrganizationMember.role == Role.OWNER.value)
            .first()
        )
        if owner is None or organization is None:
            assert False

        self.assertEqual(transaction_hash, organization.org_state[0].transaction_hash)
        self.assertEqual(wallet_address, owner.address)
        self.assertEqual(nonce, organization.org_state[0].nonce)

    def tearDown(self):
        org_repo.session.query(Group).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(OrganizationState).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Organization).delete()
        org_repo.session.commit()
