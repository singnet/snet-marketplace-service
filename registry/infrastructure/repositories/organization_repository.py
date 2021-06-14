from datetime import datetime
from uuid import uuid4

from registry.constants import Role, OrganizationMemberStatus, OrganizationStatus, VerificationStatus
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.exceptions import OrganizationNotFoundException
from registry.infrastructure.models import Organization, OrganizationMember, OrganizationState, Group, \
    OrganizationAddress, OrganizationArchive
from registry.infrastructure.repositories.base_repository import BaseRepository


class OrganizationPublisherRepository(BaseRepository):

    def get_org(self, status=None, limit=None, org_type=None):
        organization_query = self.session.query(Organization)
        if status is not None:
            organization_query = organization_query \
                .join(OrganizationState, Organization.uuid == OrganizationState.org_uuid) \
                .filter(OrganizationState.state == status)
        if org_type is not None:
            organization_query = organization_query.filter(Organization.org_type == org_type)
        if limit is not None:
            organization_query = organization_query.limit(limit)
        organizations = organization_query.all()
        organization_domain_entity = OrganizationFactory.org_domain_entity_from_repo_model_list(organizations)
        self.session.commit()
        return organization_domain_entity

    def get_org_for_org_uuid(self, org_uuid):
        organization = self.session.query(Organization).filter(Organization.uuid == org_uuid).first()
        if organization is None:
            raise OrganizationNotFoundException()
        organization_domain_entity = OrganizationFactory.org_domain_entity_from_repo_model(organization)
        self.session.commit()
        return organization_domain_entity

    def get_org_for_org_id(self, org_id):
        organization = self.session.query(Organization).filter(Organization.org_id == org_id).first()
        if organization is None:
            raise OrganizationNotFoundException()
        organization_domain_entity = OrganizationFactory.org_domain_entity_from_repo_model(organization)
        self.session.commit()
        return organization_domain_entity

    def get_org_for_user(self, username):
        organizations = self.session.query(Organization) \
            .join(OrganizationMember, Organization.uuid == OrganizationMember.org_uuid) \
            .filter(OrganizationMember.username == username).all()
        organizations_domain_entity = OrganizationFactory.org_domain_entity_from_repo_model_list(organizations)
        self.session.commit()
        return organizations_domain_entity

    def get_groups_for_org(self, org_uuid):
        groups = self.session.query(Group).filter(Group.org_uuid == org_uuid).all()
        groups_domain_entity = OrganizationFactory.parse_group_data_model(groups)
        self.session.commit()
        return groups_domain_entity

    def store_ipfs_hash(self, organization, username):
        organization_db_model = self.session.query(Organization).filter(Organization.uuid == organization.uuid).first()
        organization_db_model.assets = organization.assets
        organization_db_model.metadata_ipfs_uri = organization.metadata_ipfs_uri
        organization_db_model.org_state[0].updated_on = datetime.utcnow()
        organization_db_model.org_state[0].updated_by = username
        self.session.commit()

    def persist_publish_org_transaction_hash(self, org_uuid, transaction_hash, wallet_address, nonce, username):
        organization_db_model = self.session.query(Organization).filter(Organization.uuid == org_uuid).first()
        org_owner = self.session.query(OrganizationMember).filter(OrganizationMember.role == Role.OWNER.value) \
            .filter(OrganizationMember.org_uuid == org_uuid).first()
        if organization_db_model is None or org_owner is None:
            raise OrganizationNotFoundException()
        try:
            organization_db_model.org_state[0].wallet_address = wallet_address
            organization_db_model.org_state[0].state = OrganizationStatus.PUBLISH_IN_PROGRESS.value
            organization_db_model.org_state[0].updated_on = datetime.utcnow()
            organization_db_model.org_state[0].updated_by = username
            organization_db_model.org_state[0].transaction_hash = transaction_hash
            organization_db_model.org_state[0].nonce = nonce
            org_owner.address = wallet_address
            org_owner.transaction_hash = transaction_hash
            if org_owner != OrganizationMemberStatus.PUBLISHED.value:
                org_owner.status = OrganizationMemberStatus.PUBLISH_IN_PROGRESS.value
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def store_organization(self, organization, username, state, test_transaction_hash=None):
        organization_db_model = self.session.query(Organization).filter(
            Organization.uuid == organization.uuid).first()
        if state in [OrganizationStatus.DRAFT.value, OrganizationStatus.APPROVAL_PENDING.value,
                     OrganizationStatus.PUBLISHED_UNAPPROVED.value]:
            if organization_db_model is None:
                self.add_organization(organization, username, state, test_transaction_hash=test_transaction_hash)
            else:
                self._update_organization(organization_db_model, organization, username, state,
                                          test_transaction_hash=test_transaction_hash)

    def update_organization(self, organization, username, state, test_transaction_hash=None):
        organization_db_model = self.session.query(Organization).filter(
            Organization.uuid == organization.uuid).first()
        if organization_db_model is None:
            raise OrganizationNotFoundException()
        self._update_organization(organization_db_model, organization, username, state,
                                  test_transaction_hash=test_transaction_hash)

    def update_organization_status(self, org_uuid, status, updated_by, comment=None):
        try:
            organization = self.session.query(Organization).filter(Organization.uuid == org_uuid).first()
            if organization.org_state[0].state in [OrganizationStatus.ONBOARDING.value,
                                                   OrganizationStatus.ONBOARDING_REJECTED.value,
                                                   OrganizationStatus.ONBOARDING_APPROVED.value]:
                if status == OrganizationStatus.REJECTED.value:
                    status = OrganizationStatus.ONBOARDING_REJECTED.value
                elif status == OrganizationStatus.APPROVED.value:
                    status = OrganizationStatus.ONBOARDING_APPROVED.value
            organization.org_state[0].state = status
            organization.org_state[0].updated_by = updated_by
            organization.org_state[0].updated_on = datetime.utcnow()
            if comment is not None:
                comments = list(organization.org_state[0].comments)
                comments.append(comment.to_dict())
                organization.org_state[0].comments = comments
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def add_organization(self, organization, username, state, address="", test_transaction_hash=None):
        current_time = datetime.utcnow()
        org_addresses_domain_entity = organization.addresses
        group_domain_entity = organization.groups

        groups = [
            Group(name=group.name, id=group.group_id, org_uuid=organization.uuid,
                  payment_address=group.payment_address, payment_config=group.payment_config, status=group.status)
            for group in group_domain_entity]

        addresses = [
            OrganizationAddress(
                org_uuid=organization.uuid, address_type=address.address_type, street_address=address.street_address,
                apartment=address.apartment, city=address.city, pincode=address.pincode, state=address.state,
                country=address.country, created_on=current_time, updated_on=current_time
            )
            for address in org_addresses_domain_entity]

        org_state = [
            OrganizationState(
                org_uuid=organization.uuid, state=state, transaction_hash="", wallet_address="",
                created_by=username, created_on=current_time, test_transaction_hash=test_transaction_hash,
                updated_by=username, updated_on=current_time, reviewed_by="")]

        self.add_item(Organization(
            uuid=organization.uuid, name=organization.name, org_id=organization.id,
            org_type=organization.org_type, origin=organization.origin, description=organization.description,
            short_description=organization.short_description, url=organization.url,
            duns_no=organization.duns_no, contacts=organization.contacts,
            assets=organization.assets, metadata_ipfs_uri=organization.metadata_ipfs_uri,
            org_state=org_state, groups=groups, addresses=addresses
        ))

        self.add_item(OrganizationMember(
            invite_code=uuid4().hex, org_uuid=organization.uuid, role=Role.OWNER.value, username=username,
            address=address, status=OrganizationMemberStatus.ACCEPTED.value, transaction_hash="",
            invited_on=current_time, created_on=current_time, updated_on=current_time))

    def _update_organization(self, organization_db_model, organization, username, state, test_transaction_hash=None):
        current_time = datetime.utcnow()
        organization_db_model.name = organization.name
        organization_db_model.org_id = organization.id
        organization_db_model.org_type = organization.org_type
        organization_db_model.origin = organization.origin
        organization_db_model.description = organization.description
        organization_db_model.short_description = organization.short_description
        organization_db_model.url = organization.url
        organization_db_model.duns_no = organization.duns_no
        organization_db_model.contacts = organization.contacts
        organization_db_model.assets = organization.assets
        organization_db_model.metadata_ipfs_uri = organization.metadata_ipfs_uri
        organization_db_model.org_state[0].state = state
        organization_db_model.org_state[0].updated_on = current_time
        if test_transaction_hash is not None:
            organization_db_model.org_state[0].test_transaction_hash = test_transaction_hash
        organization_db_model.org_state[0].updated_by = username
        self.session.commit()

        org_addresses_domain_entity = organization.addresses
        group_domain_entity = organization.groups
        addresses = [
            OrganizationAddress(
                org_uuid=organization.uuid, address_type=address.address_type, street_address=address.street_address,
                apartment=address.apartment, city=address.city, pincode=address.pincode, state=address.state,
                country=address.country, created_on=current_time, updated_on=current_time
            )
            for address in org_addresses_domain_entity]

        groups = [
            Group(name=group.name, id=group.group_id, org_uuid=organization.uuid,
                  payment_address=group.payment_address, payment_config=group.payment_config, status=group.status)
            for group in group_domain_entity]

        self.session.query(OrganizationAddress).filter(OrganizationAddress.org_uuid == organization.uuid) \
            .delete(synchronize_session='fetch')
        self.session.query(Group).filter(Group.org_uuid == organization.uuid).delete(synchronize_session='fetch')
        self.session.commit()

        self.add_all_items(addresses)
        self.add_all_items(groups)

    def add_organization_archive(self, organization):
        groups = [group.to_dict() for group in organization.groups]
        org_state = organization.org_state.to_dict()
        self.add_item(OrganizationArchive(
            uuid=organization.uuid, name=organization.name, org_id=organization.id,
            org_type=organization.org_type, origin=organization.origin, description=organization.description,
            short_description=organization.short_description, url=organization.url,
            duns_no=organization.duns_no, contacts=organization.contacts,
            assets=organization.assets, metadata_ipfs_uri=organization.metadata_ipfs_uri,
            org_state=org_state, groups=groups
        ))

    def get_org_member(self, username=None, org_uuid=None, role=None, status=None, invite_code=None):
        org_member_query = self.session.query(OrganizationMember)
        if org_uuid is not None:
            org_member_query = org_member_query.filter(OrganizationMember.org_uuid == org_uuid)
        if invite_code is not None:
            org_member_query = org_member_query.filter(OrganizationMember.invite_code == invite_code)
        if username is not None:
            org_member_query = org_member_query.filter(OrganizationMember.username == username)
        if role is not None:
            org_member_query = org_member_query.filter(OrganizationMember.role == role)
        if status is not None:
            org_member_query = org_member_query.filter(OrganizationMember.status == status)

        org_member = org_member_query.all()
        org_member_domain_entity = []
        if len(org_member) > 0:
            org_member_domain_entity = OrganizationFactory.org_member_domain_from_repo_model_list(org_member)
        self.session.commit()
        return org_member_domain_entity

    def add_member(self, org_member):
        member_db_models = []
        current_time = datetime.utcnow()
        for member in org_member:
            member_db_models.append(
                OrganizationMember(
                    org_uuid=member.org_uuid,
                    role=member.role,
                    status=member.status,
                    address=member.address,
                    transaction_hash=member.transaction_hash,
                    username=member.username,
                    invite_code=member.invite_code,
                    updated_on=member.updated_on,
                    invited_on=member.invited_on,
                    created_on=current_time
                )
            )
        self.add_all_items(member_db_models)

    def org_member_verify(self, username, invite_code):
        org_members = self.session.query(OrganizationMember) \
            .filter(OrganizationMember.invite_code == invite_code) \
            .filter(OrganizationMember.username == username) \
            .filter(OrganizationMember.status == OrganizationMemberStatus.PENDING.value) \
            .all()
        if len(org_members) == 0:
            self.session.commit()
            return False
        self.session.commit()
        return True

    def delete_members(self, org_member_list, member_status):
        member_username_list = [member.username for member in org_member_list]
        self.session.query(OrganizationMember).filter(OrganizationMember.username.in_(member_username_list)) \
            .filter(OrganizationMember.status.in_(member_status)).delete(synchronize_session='fetch')
        self.session.commit()

    def delete_published_members(self, member_list):
        member_address_list = [member.address for member in member_list]
        self.session.query(OrganizationMember).filter(OrganizationMember.address.in_(member_address_list)) \
            .filter(OrganizationMember.status == OrganizationMemberStatus.PUBLISHED.value)\
            .delete(synchronize_session='fetch')
        self.session.commit()

    def persist_publish_org_member_transaction_hash(self, org_member, transaction_hash, org_uuid):
        member_username_list = [member.username for member in org_member]
        org_members_db_items = self.session.query(OrganizationMember) \
            .filter(OrganizationMember.username.in_(member_username_list)) \
            .filter(OrganizationMember.status == OrganizationMemberStatus.ACCEPTED.value) \
            .filter(OrganizationMember.org_uuid == org_uuid)
        for org_member in org_members_db_items:
            org_member.status = OrganizationMemberStatus.PUBLISH_IN_PROGRESS.value
            org_member.transaction_hash = transaction_hash
            org_member.updated_on = datetime.utcnow()
        self.session.commit()

    def update_org_member(self, username, wallet_address, invite_code):
        org_member = self.session.query(OrganizationMember) \
            .filter(OrganizationMember.invite_code == invite_code) \
            .filter(OrganizationMember.username == username) \
            .filter(OrganizationMember.status == OrganizationMemberStatus.PENDING.value) \
            .first()
        if org_member is None:
            raise Exception(f"No member found")

        if org_member.status == OrganizationMemberStatus.PUBLISHED.value and org_member.address == wallet_address:
            org_member.username = username
        elif org_member.status == OrganizationMemberStatus.PENDING.value and org_member.username == username:
            org_member.address = wallet_address
            org_member.status = OrganizationMemberStatus.ACCEPTED.value
        org_member.updated_on = datetime.utcnow()
        self.session.commit()

    def update_org_member_using_address(self, org_uuid, member, wallet_address):
        org_member = self.session.query(OrganizationMember) \
            .filter(OrganizationMember.address == wallet_address) \
            .filter(OrganizationMember.org_uuid == org_uuid) \
            .first()
        if org_member is None:
            raise Exception(f"No existing member found")

        org_member.status = member.status
        org_member.updated_on = datetime.utcnow()
        self.session.commit()

    def update_all_individual_organization_for_user(self, username, status, updated_by):
        organizations_db = self.session.query(Organization) \
            .join(OrganizationMember, Organization.uuid == OrganizationMember.org_uuid) \
            .filter(OrganizationMember.username == username).filter(OrganizationMember.role == Role.OWNER.value).all()
        for organization in organizations_db:
            if organization.org_state[0].state == OrganizationStatus.ONBOARDING.value:
                if status == VerificationStatus.APPROVED.value:
                    updated_status = OrganizationStatus.ONBOARDING_APPROVED.value
                elif status == VerificationStatus.REJECTED.value:
                    updated_status = OrganizationStatus.ONBOARDING_REJECTED.value
                else:
                    raise Exception("Invalid verification status")
                organization.org_state[0].updated_by = updated_by
                organization.org_state[0].updated_at = datetime.utcnow()
                organization.org_state[0].state = updated_status
        self.session.commit()

    def get_org_state_with_status(self, status):
        organization_state_db = self.session.query(OrganizationState).filter(OrganizationState.state == status).all()
        organization_state = OrganizationFactory.parse_organization_state_from_db_list(organization_state_db)
        self.session.commit()
        return organization_state

    def update_org_status(self, org_uuid_list, prev_state, next_state):
        self.session.query(OrganizationState).filter(OrganizationState.org_uuid.in_(org_uuid_list)).filter(
            OrganizationState.state == prev_state).update({OrganizationState.state: next_state},
                                                          synchronize_session=False)
        self.session.commit()
