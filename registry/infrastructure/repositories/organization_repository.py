from datetime import datetime

from sqlalchemy import desc

from registry.constants import OrganizationStatus
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.models.models import Group, OrganizationReviewWorkflow, \
    OrganizationHistory, OrganizationMember, OrganizationAddress, OrganizationAddressHistory
from registry.infrastructure.models.models import Organization
from registry.infrastructure.repositories.base_repository import BaseRepository
from datetime import datetime as dt
from common.logger import get_logger

logger = get_logger(__name__)


class OrganizationRepository(BaseRepository):

    def draft_update_org(self, organization, username):
        current_drafts = self.get_org_with_status(organization.org_uuid, OrganizationStatus.DRAFT.value)
        if len(current_drafts) > 0:
            self.update_org_draft(current_drafts[0], organization, username)
        else:
            self.add_org_with_status(organization, OrganizationStatus.DRAFT.value, username)

    def add_org_with_status(self, organization, status, username):
        current_time = datetime.utcnow()
        address = list(OrganizationAddress(
            headquater_address=organization.get_address()["headquater_address"],
            mailing_address=organization.get_address()["mailing_address"],
            created_on=current_time,
            updated_on=current_time,
        ))
        groups = organization.groups
        group_data = self.group_data_items_from_group_list(groups, organization.org_uuid)
        organization_item = Organization(
            name=organization.name,
            org_uuid=organization.org_uuid,
            org_id=organization.org_id,
            type=organization.org_type,
            description=organization.description,
            short_description=organization.short_description,
            url=organization.url,
            contacts=organization.contacts,
            assets=organization.assets,
            metadata_ipfs_hash=organization.metadata_ipfs_hash,
            groups=group_data,
            duns_no=organization.get_duns_no(),
            address=address,
        )
        self.add_item(organization_item)
        org_row_id = organization_item.row_id

        self.add_item(
            OrganizationReviewWorkflow(
                org_row_id=org_row_id,
                status=status,
                created_by=username,
                updated_by=username,
                create_on=current_time,
                updated_on=current_time,
            )
        )
        self.session.commit()

    def update_org_draft(self, current_draft, organization, username):
        current_draft.Organization.name = organization.name
        current_draft.Organization.org_id = organization.org_id
        current_draft.Organization.type = organization.org_type
        current_draft.Organization.description = organization.description
        current_draft.Organization.short_description = organization.short_description
        current_draft.Organization.url = organization.url
        current_draft.Organization.contacts = organization.contacts
        current_draft.Organization.assets = organization.assets
        current_draft.Organization.metadata_ipfs_hash = organization.metadata_ipfs_hash
        current_draft.Organization.duns_no = organization.get_duns_no()
        current_draft.OrganizationReviewWorkflow.updated_by = username
        current_draft.OrganizationReviewWorkflow.updated_on = datetime.utcnow()
        current_draft.Organization.address = OrganizationAddress(
            headquater_address=organization.get_address()["headquater_address"],
            mailing_address=organization.get_address()["mailing_address"],
            created_on=datetime.utcnow(),
            updated_on=datetime.utcnow(),)
        self.session.commit()

    def get_organization_draft(self, org_uuid):
        organizations = self.get_org_with_status(org_uuid, OrganizationStatus.DRAFT.value)
        return OrganizationFactory.parse_organization_workflow_data_model_list(organizations)

    def get_approved_org(self, org_uuid):
        organizations = self.get_org_with_status(org_uuid, OrganizationStatus.APPROVED.value)
        return OrganizationFactory.parse_organization_workflow_data_model_list(organizations)

    def get_org_with_status(self, org_uuid, status):
        organizations = self.session.query(Organization, OrganizationReviewWorkflow, OrganizationAddress) \
            .join(OrganizationReviewWorkflow, OrganizationReviewWorkflow.org_row_id == Organization.row_id) \
            .join(OrganizationAddress, OrganizationAddress.org_row_id == Organization.row_id) \
            .filter(Organization.org_uuid == org_uuid) \
            .filter(OrganizationReviewWorkflow.status == status).all()
        return organizations

    def get_org_for_uuid(self, org_uuid):
        organizations = self.session.query(Organization, OrganizationReviewWorkflow) \
            .join(OrganizationReviewWorkflow, OrganizationReviewWorkflow.org_row_id == Organization.row_id) \
            .filter(Organization.org_uuid == org_uuid).all()
        return organizations

    def move_non_published_org_to_history(self, org_uuid):
        orgs_with_status = self.session.query(Organization) \
            .join(OrganizationReviewWorkflow, Organization.row_id == OrganizationReviewWorkflow.org_row_id) \
            .filter(Organization.org_uuid == org_uuid) \
            .filter(OrganizationReviewWorkflow.status == OrganizationStatus.APPROVAL_PENDING.value) \
            .filter(OrganizationReviewWorkflow.status == OrganizationStatus.APPROVED.value).all()
        self.move_organizations_to_history(orgs_with_status)

    def move_organizations_to_history(self, organizations):
        if len(organizations) > 0:
            org_history = []
            org_address_history = []
            row_ids = []
            for org in organizations:
                row_ids.append(org.row_id)
                address = OrganizationAddressHistory(
                    row_id=org.address.row_id,
                    headquater_address=org.address.headquater_address,
                    mailing_address=org.address.mailing_address,
                    created_on=dt.utcnow(),
                    updated_on=dt.utcnow(),
                )
                org_history.append(OrganizationHistory(
                    row_id=org.row_id,
                    name=org.name,
                    org_uuid=org.org_uuid,
                    org_id=org.org_id,
                    type=org.type,
                    description=org.description,
                    short_description=org.short_description,
                    url=org.url,
                    contacts=org.contacts,
                    assets=org.assets,
                    metadata_ipfs_hash=org.metadata_ipfs_hash,
                    address=address,
                ))
                # org_address_history.append()

            self.add_all_items(org_history)
            self.session.query(Organization).filter(Organization.row_id.in_(row_ids)) \
                .delete(synchronize_session='fetch')
            self.session.commit()

    def move_org_to_history_with_status(self, org_uuid, status):
        orgs_with_status = self.session.query(Organization) \
            .join(OrganizationReviewWorkflow, Organization.row_id == OrganizationReviewWorkflow.org_row_id) \
            .filter(Organization.org_uuid == org_uuid) \
            .filter(OrganizationReviewWorkflow.status == status).all()
        self.move_organizations_to_history(orgs_with_status)

    def get_organization_for_user(self, username):
        subquery = self.session.query(Organization) \
            .join(OrganizationMember, Organization.org_uuid == OrganizationMember.org_uuid) \
            .filter(OrganizationMember.username == username).subquery()
        organizations = self.session.query(
            subquery.c.row_id.label("row_id"),
            subquery.c.name.label("name"),
            subquery.c.org_uuid.label("org_uuid"),
            subquery.c.org_id.label("org_id"),
            subquery.c.type.label("type"),
            subquery.c.description.label("description"),
            subquery.c.short_description.label("short_description"),
            subquery.c.url.label("url"),
            subquery.c.contacts.label("contacts"),
            subquery.c.metadata_ipfs_hash.label("metadata_ipfs_hash"),
            OrganizationReviewWorkflow
        ).join(OrganizationReviewWorkflow, subquery.c.row_id == OrganizationReviewWorkflow.org_row_id).all()
        return organizations

    def get_published_organization(self):
        organization = self.session.query(Organization) \
            .join(OrganizationReviewWorkflow, Organization.row_id == OrganizationReviewWorkflow.org_row_id) \
            .filter(OrganizationReviewWorkflow == OrganizationStatus.PUBLISHED.value)
        return OrganizationFactory.parse_organization_data_model_list(organization)

    def change_org_status(self, org_uuid, current_status, new_status, username):
        organizations = self.get_org_with_status(org_uuid, current_status)
        if len(organizations) > 0:
            self._update_org_status(organizations[0], new_status, username)
            self.session.commit()
        else:
            raise Exception(f"DRAFT for organization {org_uuid} not found")

    def _update_org_status(self, org_workflow_model, status, username):
        current_utc_time = datetime.utcnow()
        org_workflow_model.OrganizationReviewWorkflow.status = status
        org_workflow_model.OrganizationReviewWorkflow.updated_on = current_utc_time
        org_workflow_model.OrganizationReviewWorkflow.updated_by = username

    def add_group(self, groups, org_uuid, username):
        organizations = self.get_latest_org_from_org_uuid(org_uuid)
        if len(organizations) == 0:
            raise Exception(f"No org data for the org_uuid {org_uuid}")
        org = organizations[0]
        if org.OrganizationReviewWorkflow.status == OrganizationStatus.DRAFT.value:
            self.add_new_draft_groups_in_draft_org(groups, org, username)
        elif org.OrganizationReviewWorkflow.status == OrganizationStatus.APPROVAL_PENDING.value:
            self.add_new_draft_groups_in_draft_org(groups, org, username)
            self.move_org_to_history_with_status(org_uuid, OrganizationStatus.APPROVAL_PENDING.value)
        elif org.OrganizationReviewWorkflow.status == OrganizationStatus.APPROVED.value:
            self.add_new_draft_groups_in_draft_org(groups, org, username)
            self.move_org_to_history_with_status(org_uuid, OrganizationStatus.APPROVED.value)
        else:
            self.add_new_draft_groups_in_org(groups, org, username)

    def get_latest_org_from_org_uuid(self, org_uuid):
        organizations = self.session.query(Organization, OrganizationReviewWorkflow) \
            .join(OrganizationReviewWorkflow, OrganizationReviewWorkflow.org_row_id == Organization.row_id) \
            .filter(Organization.org_uuid == org_uuid) \
            .order_by(desc(OrganizationReviewWorkflow.updated_on)).all()
        return organizations

    def add_new_draft_groups_in_draft_org(self, groups, organization, username):
        org_row_id = organization.Organization.row_id
        self.session.query(Group).filter(Group.org_row_id == org_row_id).delete()
        self.session.commit()
        groups = [Group(
            org_row_id=org_row_id,
            org_uuid=organization.Organization.org_uuid, id=group.group_id, name=group.name,
            payment_config=group.payment_config, payment_address=group.payment_address, status=""
        ) for group in groups]
        organization.OrganizationReviewWorkflow.updated_on = datetime.utcnow()
        organization.OrganizationReviewWorkflow.updated_by = username
        self.add_all_items(groups)
        self.session.commit()

    def group_data_items_from_group_list(self, groups, org_uuid):
        group_data = []
        for group in groups:
            group_data.append(Group(
                name=group.name, id=group.group_id, org_uuid=org_uuid,
                payment_address=group.payment_address,
                payment_config=group.payment_config, status=""
            ))
        return group_data

    def add_new_draft_groups_in_org(self, groups, organization, username):
        current_time = datetime.utcnow()
        organization = organization.Organization
        group_data = self.group_data_items_from_group_list(groups, organization.org_uuid)

        organization_item = Organization(
            name=organization.name,
            org_uuid=organization.org_uuid,
            org_id=organization.org_id,
            type=organization.type,
            description=organization.description,
            short_description=organization.short_description,
            url=organization.url,
            contacts=organization.contacts,
            assets=organization.assets,
            metadata_ipfs_hash=organization.metadata_ipfs_hash,
            groups=group_data
        )
        self.add_item(organization_item)
        org_row_id = organization_item.row_id

        self.add_item(
            OrganizationReviewWorkflow(
                org_row_id=org_row_id,
                status=OrganizationStatus.DRAFT.value,
                created_by=username,
                updated_by=username,
                create_on=current_time,
                updated_on=current_time,
            )
        )
        self.session.commit()
