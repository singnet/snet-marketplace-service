from datetime import datetime
from uuid import uuid4

from registry.constants import Role, OrganizationMemberStatus, OrganizationStatus
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.exceptions import OrganizationNotFoundException
from registry.infrastructure.models import Organization, OrganizationMember, OrganizationState, Group, \
    OrganizationAddress
from registry.infrastructure.repositories.base_repository import BaseRepository


class OrganizationPublisherRepository(BaseRepository):

    def get_org(self, org_uuid):
        organization = self.session.query(Organization).filter(Organization.uuid == org_uuid).first()
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
        organization_db_model.metadata_ipfs_hash = organization.metadata_ipfs_hash
        organization_db_model.org_state[0].updated_on = datetime.utcnow()
        organization_db_model.org_state[0].updated_by = username
        self.session.commit()

    def persist_publish_org_transaction_hash(self, org_uuid, transaction_hash, wallet_address, username):
        organization_db_model = self.session.query(Organization).filter(Organization.uuid == org_uuid).first()
        if organization_db_model is None:
            raise OrganizationNotFoundException()
        organization_db_model.org_state[0].trasaction_hash = transaction_hash
        organization_db_model.org_state[0].wallet_address = wallet_address
        organization_db_model.org_state[0].state = OrganizationStatus.PUBLISH_IN_PROGRESS.value
        organization_db_model.org_state[0].updated_on = datetime.utcnow()
        organization_db_model.org_state[0].updated_by = username
        self.session.commit()

    def store_organization(self, organization, username, state):
        organization_db_model = self.session.query(Organization).filter(
            Organization.uuid == organization.uuid).first()
        if state in [OrganizationStatus.DRAFT.value, OrganizationStatus.APPROVAL_PENDING.value]:
            if organization_db_model is None:
                self.add_organization(organization, username, state)
            else:
                self.update_organization(organization_db_model, organization, username, state)

    def add_organization(self, organization, username, state):
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
                org_uuid=organization.uuid, state=state, transaction_hash="",
                wallet_address="", created_by=username, created_on=current_time,
                updated_by=username, updated_on=current_time, reviewed_by="")]

        self.add_item(Organization(
            uuid=organization.uuid, name=organization.name, org_id=organization.id,
            org_type=organization.org_type, origin=organization.origin, description=organization.description,
            short_description=organization.short_description, url=organization.url,
            duns_no=organization.duns_no, contacts=organization.contacts, assets=organization.assets,
            metadata_ipfs_hash=organization.metadata_ipfs_hash, org_state=org_state, groups=groups, addresses=addresses
        ))

        self.add_item(OrganizationMember(
            invite_code=uuid4().hex, org_uuid=organization.uuid, role=Role.OWNER.value, username=username, address="",
            status=OrganizationMemberStatus.ACCEPTED.value, transaction_hash="", invited_on=current_time,
            created_on=current_time, updated_on=current_time))

    def update_organization(self, organization_db_model, organization, username, state):
        current_time = datetime.utcnow()
        organization_db_model.name = organization.name
        organization_db_model.id = organization.id
        organization_db_model.org_type = organization.org_type
        organization_db_model.origin = organization.origin
        organization_db_model.description = organization.description
        organization_db_model.short_description = organization.short_description
        organization_db_model.url = organization.url
        organization_db_model.duns_no = organization.duns_no
        organization_db_model.contacts = organization.contacts
        organization_db_model.assets = organization.assets
        organization_db_model.metadata_ipfs_hash = organization.metadata_ipfs_hash
        organization_db_model.org_state[0].state = state
        organization_db_model.org_state[0].updated_on = current_time
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

        self.session.query(OrganizationAddress).filter(OrganizationAddress.org_uuid == organization.uuid).delete(synchronize_session='fetch')
        self.session.query(Group).filter(Group.org_uuid == organization.uuid).delete(synchronize_session='fetch')
        self.session.commit()

        self.add_all_items(addresses)
        self.add_all_items(groups)

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

    def delete_members(self, org_member_list):
        allowed_delete_member_status = [OrganizationMemberStatus.PENDING.value,
                                        OrganizationMemberStatus.ACCEPTED.value]
        member_username_list = [member.username for member in org_member_list]
        self.session.query(OrganizationMember).filter(OrganizationMember.username.in_(member_username_list)) \
            .filter(OrganizationMember.status.in_(allowed_delete_member_status)).delete(synchronize_session='fetch')
        self.session.commit()

    def persist_publish_org_member_transaction_hash(self, org_member, transaction_hash, org_uuid):
        member_username_list = [member.username for member in org_member]
        org_members_db_items = self.session.query(OrganizationMember) \
            .filter(OrganizationMember.username.in_(member_username_list))\
            .filter(OrganizationMember.status == OrganizationMemberStatus.ACCEPTED.value)\
            .filter(OrganizationMember.org_uuid == org_uuid)
        for org_member in org_members_db_items:
            org_member.status = OrganizationMemberStatus.PUBLISH_IN_PROGRESS.value
            org_member.transaction_hash = transaction_hash
            org_member.updated_on = datetime.utcnow()
        self.session.commit()

    def update_org_member(self, username, wallet_address, invite_code):
        org_member = self.session.query(OrganizationMember)\
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
