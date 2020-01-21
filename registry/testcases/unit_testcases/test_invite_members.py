from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from registry.application.services.organization_publisher_service import org_repo, OrganizationService
from registry.constants import OrganizationStatus, OrganizationMemberStatus, Role
from registry.domain.models.group import Group as DomainGroup
from registry.domain.models.organization import Organization as DomainOrganization
from registry.infrastructure.models.models import OrganizationMember, OrganizationHistory, OrganizationReviewWorkflow, \
    Organization, OrganizationAddress, Group, GroupHistory

ORIGIN = "PUBLISHER_DAPP"


class TestInviteMembers(TestCase):

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_invite_members(self, mock_invoke_lambda):
        mock_invoke_lambda.return_value = None
        test_org_id = uuid4().hex
        owner_invite_code = uuid4().hex
        owner_wallet_address = "0x123"
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, origin=ORIGIN, groups=[], addresses=[], status=OrganizationStatus.APPROVAL_PENDING.value,
            owner_name="Dummy Name")
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, username)
        org_repo.add_item(
            OrganizationMember(
                username=username,
                org_uuid=test_org_id,
                role=Role.OWNER.value,
                address=owner_wallet_address,
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x123",
                invite_code=owner_invite_code
            )
        )
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
        OrganizationService(test_org_id, username).invite_members(new_org_members)
        invited_org_members = org_repo.get_members_for_given_org(test_org_id, OrganizationMemberStatus.PENDING.value)
        if len(invited_org_members) == 3:
            assert True
        else:
            assert False

    @patch("common.boto_utils.BotoUtils.invoke_lambda")
    def test_invite_members_two(self, mock_invoke_lambda):
        """ invite same member twice """
        mock_invoke_lambda.return_value = None
        test_org_id = uuid4().hex
        owner_invite_code = uuid4().hex
        owner_wallet_address = "0x123"
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, origin=ORIGIN, groups=[], addresses=[], status=OrganizationStatus.APPROVAL_PENDING.value,
            owner_name="Dummy Name")
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, username)
        org_repo.add_item(
            OrganizationMember(
                username=username,
                org_uuid=test_org_id,
                role=Role.OWNER.value,
                address=owner_wallet_address,
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x123",
                invite_code=owner_invite_code
            )
        )
        new_org_members = [
            {
                "username": "karl@dummy.io"
            }
        ]
        OrganizationService(test_org_id, username).invite_members(new_org_members)
        self.assertRaises(Exception, OrganizationService(test_org_id, username).invite_members, new_org_members)

    def test_get_member(self):
        """ adding new group without existing draft """
        test_org_id = uuid4().hex
        owner_invite_code = uuid4().hex
        owner_wallet_address = "0x123"
        username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, origin=ORIGIN, groups=[], addresses=[], status=OrganizationStatus.APPROVAL_PENDING.value,
            owner_name="Dummy Name")
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        current_time = datetime.utcnow()
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, username)
        org_repo.add_item(
            OrganizationMember(
                username=username,
                org_uuid=test_org_id,
                role=Role.OWNER.value,
                address=owner_wallet_address,
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x123",
                invite_code=owner_invite_code,
                invited_on=current_time,
                updated_on=current_time
            )
        )
        members = OrganizationService(test_org_id, username).get_member(username)
        if isinstance(members, list) and len(members) == 1:
            self.assertDictEqual(
                members[0],
                {
                    'username': 'dummy@snet.io',
                    'address': owner_wallet_address,
                    'status': 'PUBLISHED',
                    'role': 'OWNER',
                    'invited_on': current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_on": current_time.strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        else:
            assert False

    def test_publish_members(self):
        test_org_id = uuid4().hex
        owner_invite_code = uuid4().hex
        owner_wallet_address = "0x123"
        owner_username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", owner_username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, origin=ORIGIN, groups=[], addresses=[], status=OrganizationStatus.APPROVAL_PENDING.value,
            owner_name="Dummy Name")
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, owner_username)
        org_repo.add_item(
            OrganizationMember(
                username=owner_username,
                org_uuid=test_org_id,
                role=Role.OWNER.value,
                address=owner_wallet_address,
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x123",
                invite_code=owner_invite_code,
                invited_on=datetime.utcnow(),
                updated_on=datetime.utcnow()
            )
        )
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
                    org_uuid=test_org_id,
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
        OrganizationService(test_org_id, owner_username) \
            .publish_members("0x123", new_org_members)
        org_members = org_repo.session.query(OrganizationMember).filter(OrganizationMember.org_uuid == test_org_id)\
            .filter(OrganizationMember.status == OrganizationMemberStatus.PUBLISH_IN_PROGRESS.value).all()

        if len(org_members) == 3:
            assert True
        else:
            assert False

    def test_delete_members(self):
        test_org_id = uuid4().hex
        owner_invite_code = uuid4().hex
        owner_wallet_address = "0x123"
        owner_username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", owner_username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, origin=ORIGIN, groups=[], addresses=[], status=OrganizationStatus.APPROVAL_PENDING.value,
            owner_name="Dummy Name")
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, owner_username)
        org_repo.add_item(
            OrganizationMember(
                username=owner_username,
                org_uuid=test_org_id,
                role=Role.OWNER.value,
                address=owner_wallet_address,
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x123",
                invite_code=owner_invite_code,
                invited_on=datetime.utcnow(),
                updated_on=datetime.utcnow()
            )
        )
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
                    org_uuid=test_org_id,
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
        OrganizationService(test_org_id, owner_username).delete_members(new_org_members)
        org_members = org_repo.session.query(OrganizationMember).filter(OrganizationMember.org_uuid == test_org_id).all()

        if len(org_members) == 1:
            assert True
        else:
            assert False

    def test_verify_invite(self):
        test_org_id = uuid4().hex
        owner_invite_code = uuid4().hex
        owner_wallet_address = "0x123"
        owner_username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", owner_username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, origin=ORIGIN, groups=[], addresses=[], status=OrganizationStatus.APPROVAL_PENDING.value,
            owner_name="Dummy Name")
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, owner_username)
        org_repo.add_item(
            OrganizationMember(
                username=owner_username,
                org_uuid=test_org_id,
                role=Role.OWNER.value,
                address=owner_wallet_address,
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x123",
                invite_code=owner_invite_code,
                invited_on=datetime.utcnow(),
                updated_on=datetime.utcnow()
            )
        )
        member_username = "karl@dummy.io"
        member_invite_code = uuid4().hex
        org_repo.add_item(
            OrganizationMember(
                username=member_username,
                org_uuid=test_org_id,
                role=Role.MEMBER.value,
                address="0x123",
                status=OrganizationMemberStatus.PENDING.value,
                transaction_hash="0x123",
                invite_code=member_invite_code,
                invited_on=datetime.utcnow(),
                updated_on=datetime.utcnow()
            )
        )
        self.assertEqual(OrganizationService(None, member_username).verify_invite(member_invite_code), "OK")
        self.assertEqual(OrganizationService(None, member_username).verify_invite("1234"), "NOT_FOUND")

    def test_register_member(self):
        test_org_id = uuid4().hex
        owner_invite_code = uuid4().hex
        owner_wallet_address = "0x123"
        owner_username = "dummy@snet.io"
        organization = DomainOrganization(
            "dummy_org", "org_id", test_org_id, "organization", owner_username,
            "that is the dummy org for testcases", "that is the short description", "dummy.com", [], {}, "",
            duns_no=12345678, origin=ORIGIN, groups=[], addresses=[], status=OrganizationStatus.APPROVAL_PENDING.value,
            owner_name="Dummy Name")
        organization.add_group(DomainGroup(
            name="my-group",
            group_id="group_id",
            payment_address="0x123",
            payment_config={},
            status=''
        ))
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISHED.value, owner_username)
        org_repo.add_item(
            OrganizationMember(
                username=owner_username,
                org_uuid=test_org_id,
                role=Role.OWNER.value,
                address=owner_wallet_address,
                status=OrganizationMemberStatus.PUBLISHED.value,
                transaction_hash="0x123",
                invite_code=owner_invite_code,
                invited_on=datetime.utcnow(),
                updated_on=datetime.utcnow()
            )
        )
        member_username = "karl@dummy.io"
        member_invite_code = uuid4().hex
        org_repo.add_item(
            OrganizationMember(
                username=member_username,
                org_uuid=test_org_id,
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
        self.assertRaises(Exception, OrganizationService(test_org_id, member_username).register_member, "0x9876")
        OrganizationService(test_org_id, member_username).register_member(member_wallet_address)
        members = org_repo.session.query(OrganizationMember).filter(OrganizationMember.org_uuid == test_org_id)\
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

    def tearDown(self):
        org_repo.session.query(Organization).delete()
        org_repo.session.query(OrganizationReviewWorkflow).delete()
        org_repo.session.query(OrganizationHistory).delete()
        org_repo.session.query(OrganizationAddress).delete()
        org_repo.session.query(Group).delete()
        org_repo.session.query(GroupHistory).delete()
        org_repo.session.query(OrganizationMember).delete()
        org_repo.session.commit()
