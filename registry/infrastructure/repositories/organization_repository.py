from datetime import datetime

from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.models.models import Group, OrganizationReviewWorkflow, \
    OrganizationHistory, OrganizationMember
from registry.infrastructure.models.models import Organization
from registry.infrastructure.repositories.base_repository import BaseRepository


class OrganizationRepository(BaseRepository):

    def draft_update_org(self, organization, username):
        current_drafts = self.get_org_with_status(organization.org_uuid, "DRAFT")
        if len(current_drafts) > 0:
            self.update_org_draft(current_drafts[0], organization, username)
        else:
            self.add_org_with_status(organization, "DRAFT", username)

    def add_org_with_status(self, organization, status, username):
        current_time = datetime.utcnow()
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
            metadata_ipfs_hash=organization.metadata_ipfs_hash
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
        current_draft.OrganizationReviewWorkflow.updated_by = username
        current_draft.OrganizationReviewWorkflow.updated_on = datetime.utcnow()
        self.session.commit()

    def get_latest_org_from_org_uuid(self, org_uuid):
        pass

    def get_organization_draft(self, org_uuid):
        organizations = self.get_org_with_status(org_uuid, "DRAFT")
        return OrganizationFactory.parse_organization_workflow_data_model_list(organizations)

    def get_approved_org(self, org_uuid):
        organizations = self.get_org_with_status(org_uuid, "APPROVED")
        return OrganizationFactory.parse_organization_workflow_data_model_list(organizations)

    def get_org_with_status(self, org_uuid, status):
        organizations = self.session.query(Organization, OrganizationReviewWorkflow) \
            .join(OrganizationReviewWorkflow, OrganizationReviewWorkflow.org_row_id == Organization.row_id) \
            .filter(Organization.org_uuid == org_uuid) \
            .filter(OrganizationReviewWorkflow.status == status).all()
        return organizations

    def export_org_with_status(self, organization, status):
        pending_approval_org = self.session.query(Organization) \
            .join(OrganizationReviewWorkflow, Organization.row_id == OrganizationReviewWorkflow.org_row_id) \
            .filter(Organization.org_uuid == organization.org_uuid) \
            .filter(OrganizationReviewWorkflow.status == status).all()
        if len(pending_approval_org) > 0:
            org_history = []
            row_ids = []
            for org in pending_approval_org:
                row_ids.append(org.row_id)
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
                    metadata_ipfs_hash=org.metadata_ipfs_hash
                ))

            self.add_all_items(org_history)
            self.session.query(Organization).filter(Organization.row_id.in_(row_ids)) \
                .delete(synchronize_session='fetch')
            self.add_all_items(org_history)
            self.session.commit()

    def get_organization_for_user(self, username):
        subquery = self.session.query(Organization)\
            .join(OrganizationMember, Organization.org_uuid == OrganizationMember.org_uuid)\
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
        organization = self.session.query(Organization)\
            .join(OrganizationReviewWorkflow, Organization.row_id == OrganizationReviewWorkflow.org_row_id)\
            .filter(OrganizationReviewWorkflow == "PUBLISHED")
        return OrganizationFactory.parse_organization_data_model_list(organization)

    def change_org_status(self, org_uuid, current_status, new_status, username):
        orgs = self.get_org_with_status(org_uuid, current_status)
        if len(orgs) > 0:
            self._update_org_status(orgs[0], new_status, username)
            self.session.commit()
        else:
            raise Exception(f"DRAFT for organization {org_uuid} not found")

    def _update_org_status(self, org_workflow_model, status, username):
        current_utc_time = datetime.utcnow()
        org_workflow_model.OrganizationReviewWorkflow.status = status
        org_workflow_model.OrganizationReviewWorkflow.updated_on = current_utc_time
        org_workflow_model.OrganizationReviewWorkflow.updated_by = username
