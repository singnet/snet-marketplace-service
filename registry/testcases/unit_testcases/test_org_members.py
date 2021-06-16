from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from registry.application.services.organization_publisher_service import org_repo, OrganizationPublisherService
from registry.constants import OrganizationMemberStatus, OrganizationStatus, Role
from registry.domain.models.organization import Organization as DomainOrganization
from registry.infrastructure.models import Group, OrganizationMember, OrganizationState, OrganizationAddress, \
    Organization
from registry.testcases.test_variables import ORG_CONTACTS
from registry.testcases.test_variables import ORIGIN


class TestOrganizationMember(TestCase):

    def test_get_all_member(self):
        test_org_uuid = uuid4().hex
        owner_username = "user@snet.io"
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid, "org_id", "org_dummy",
                "ORGANIZATION", ORIGIN, "description",
                "short_description", "https://test.io", ORG_CONTACTS, {}, "ipfs_hash", "123456879", [], [], [], []),
            owner_username, OrganizationStatus.PUBLISHED.value)

        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "nyx@dummy.io",
                "address": "0x345"
            }
        ]
        org_repo.add_all_items(
            [
                OrganizationMember(
                    username=member["username"],
                    org_uuid=test_org_uuid,
                    role=Role.MEMBER.value,
                    address=member["address"],
                    status=OrganizationMemberStatus.ACCEPTED.value,
                    transaction_hash="0x123",
                    invite_code=uuid4().hex,
                    invited_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                ) for member in new_org_members
            ]
        )
        members = OrganizationPublisherService(test_org_uuid, owner_username).get_all_member(None, Role.MEMBER.value, {})
        if len(members) == 3:
            assert True
        else:
            assert False

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_get_member(self, mock_invoke_lambda):
        test_org_uuid = uuid4().hex
        owner_username = "user@snet.io"
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid, "org_id", "org_dummy",
                "ORGANIZATION", ORIGIN, "description",
                "short_description", "https://test.io", ORG_CONTACTS, {}, "ipfs_hash", "123456879", [], [], [], []),
            owner_username, OrganizationStatus.PUBLISHED.value)

        members = OrganizationPublisherService(test_org_uuid, owner_username).get_member(owner_username)

        if isinstance(members, list) and len(members) == 1:
            members[0].pop("invited_on")
            members[0].pop("updated_on")
            self.assertDictEqual(
                members[0],
                {
                    'username': owner_username,
                    'address': "",
                    'status': 'ACCEPTED',
                    'role': 'OWNER'
                }
            )
        else:
            assert False

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_verify_invite(self, mock_invoke_lambda):
        test_org_uuid = uuid4().hex
        owner_username = "user@snet.io"
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid, "org_id", "org_dummy",
                "ORGANIZATION", ORIGIN, "description",
                "short_description", "https://test.io", ORG_CONTACTS, {}, "ipfs_hash", "123456879", [], [], [], []),
            owner_username, OrganizationStatus.PUBLISHED.value)

        member_username = "karl@dummy.io"
        member_invite_code = uuid4().hex
        org_repo.add_item(
            OrganizationMember(
                username=member_username,
                org_uuid=test_org_uuid,
                role=Role.MEMBER.value,
                address="0x123",
                status=OrganizationMemberStatus.PENDING.value,
                transaction_hash="0x123",
                invite_code=member_invite_code,
                invited_on=datetime.utcnow(),
                updated_on=datetime.utcnow()
            )
        )
        self.assertEqual(OrganizationPublisherService(None, member_username).verify_invite(member_invite_code), "OK")
        self.assertEqual(OrganizationPublisherService(None, member_username).verify_invite("1234"), "NOT_FOUND")

    def test_delete_members(self):
        test_org_uuid = uuid4().hex
        owner_username = "user@snet.io"
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid, "org_id", "org_dummy",
                "ORGANIZATION", ORIGIN, "description",
                "short_description", "https://test.io", ORG_CONTACTS, {}, "ipfs_hash", "123456879", [], [], [], []),
            owner_username, OrganizationStatus.PUBLISHED.value)

        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "nyx@dummy.io",
                "address": "0x345"
            }
        ]
        org_repo.add_all_items(
            [
                OrganizationMember(
                    username=member["username"],
                    org_uuid=test_org_uuid,
                    role=Role.MEMBER.value,
                    address=member["address"],
                    status=OrganizationMemberStatus.ACCEPTED.value,
                    transaction_hash="0x123",
                    invite_code=uuid4().hex,
                    invited_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                ) for member in new_org_members
            ]
        )
        OrganizationPublisherService(test_org_uuid, owner_username).delete_members(new_org_members)
        org_members = org_repo.session.query(OrganizationMember).filter(OrganizationMember.org_uuid == test_org_uuid).all()

        if len(org_members) == 1:
            assert True
        else:
            assert False

    def test_publish_members(self):
        test_org_uuid = uuid4().hex
        owner_username = "user@snet.io"
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid, "org_id", "org_dummy",
                "ORGANIZATION", ORIGIN, "description",
                "short_description", "https://test.io", ORG_CONTACTS, {}, "ipfs_hash", "123456879", [], [], [], []),
            owner_username, OrganizationStatus.PUBLISHED.value)

        new_org_members = [
            {
                "username": "karl@dummy.io",
                "address": "0x123"
            },
            {
                "username": "trax@dummy.io",
                "address": "0x234"
            },
            {
                "username": "nyx@dummy.io",
                "address": "0x345"
            }
        ]
        org_repo.add_all_items(
            [
                OrganizationMember(
                    username=member["username"],
                    org_uuid=test_org_uuid,
                    role=Role.MEMBER.value,
                    address=member["address"],
                    status=OrganizationMemberStatus.ACCEPTED.value,
                    transaction_hash="0x123",
                    invite_code=uuid4().hex,
                    invited_on=datetime.utcnow(),
                    updated_on=datetime.utcnow()
                ) for member in new_org_members
            ]
        )
        OrganizationPublisherService(test_org_uuid, owner_username).publish_members("0x123", new_org_members)
        org_members = org_repo.session.query(OrganizationMember).filter(OrganizationMember.org_uuid == test_org_uuid)\
            .filter(OrganizationMember.status == OrganizationMemberStatus.PUBLISH_IN_PROGRESS.value).all()

        if len(org_members) == 3:
            assert True
        else:
            assert False

    def test_register_member(self):
        test_org_uuid = uuid4().hex
        owner_username = "user@snet.io"
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid, "org_id", "org_dummy",
                "ORGANIZATION", ORIGIN, "description",
                "short_description", "https://test.io", ORG_CONTACTS, {}, "ipfs_hash", "123456879", [], [], [], []),
            owner_username, OrganizationStatus.PUBLISHED.value)

        member_username = "karl@dummy.io"
        member_invite_code = uuid4().hex
        org_repo.add_item(
            OrganizationMember(
                username=member_username,
                org_uuid=test_org_uuid,
                role=Role.MEMBER.value,
                address="",
                status=OrganizationMemberStatus.PENDING.value,
                transaction_hash="0x123",
                invite_code=member_invite_code,
                invited_on=datetime.utcnow(),
                updated_on=datetime.utcnow()
            )
        )
        member_wallet_address = "0x962FD47b5afBc8D03025cE52155890667E58dEBA"
        self.assertRaises(Exception, OrganizationPublisherService(test_org_uuid, member_username).register_member,
                          "1234", "0x9876")
        OrganizationPublisherService(test_org_uuid, member_username)\
            .register_member(member_invite_code, member_wallet_address)
        members = org_repo.session.query(OrganizationMember).filter(OrganizationMember.org_uuid == test_org_uuid)\
            .filter(OrganizationMember.username == member_username) \
            .all()
        if len(members) == 1:
            org_member = members[0]
            if org_member.status == OrganizationMemberStatus.ACCEPTED.value \
                    and org_member.address == member_wallet_address:
                assert True
            else:
                assert False
        else:
            assert False

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_invite_members(self, mock_invoke_lambda):
        mock_invoke_lambda.return_value = None
        test_org_uuid = uuid4().hex
        owner_username = "user@snet.io"
        org_repo.add_organization(
            DomainOrganization(
                test_org_uuid, "org_id", "org_dummy",
                "ORGANIZATION", ORIGIN, "description",
                "short_description", "https://test.io", ORG_CONTACTS, {}, "ipfs_hash", "123456879", [], [], [], []),
            owner_username, OrganizationStatus.PUBLISHED.value)

        new_org_members = [
            {
                "username": "karl@dummy.io"
            },
            {
                "username": "trax@dummy.io"
            },
            {
                "username": "nyx@dummy.io"
            }
        ]
        OrganizationPublisherService(test_org_uuid, owner_username).invite_members(new_org_members)
        invited_org_members = org_repo.get_org_member(org_uuid=test_org_uuid, status=OrganizationMemberStatus.PENDING.value)
        if len(invited_org_members) == 3:
            assert True
        else:
            assert False

    def tearDown(self):
        org_repo.session.query(Group).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.query(OrganizationState).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Organization).delete()
        org_repo.session.commit()
