from datetime import datetime

from registry.infrastructure.models.models import Group, OrganizationReviewWorkflow, OrganizationHistory
from registry.infrastructure.models.models import Organization
from registry.infrastructure.repositories.base_repository import BaseRepository


class OrganizationRepository(BaseRepository):

    def draft_update_org(self, organization, username):
        current_drafts = self.get_current_drafts(organization)
        if len(current_drafts) > 0:
            self.update_org_draft(current_drafts[0], organization, username)
        else:
            self.add_org_draft(organization, username)

    def add_org_draft(self, organization, username):
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
            ipfs_hash=organization.ipfs_hash
        )
        self.add_item(organization_item)
        org_row_id = organization_item.row_id

        self.add_item(
            OrganizationReviewWorkflow(
                org_row_id=org_row_id,
                status="DRAFT",
                created_by=username,
                updated_by=username,
                create_on=current_time,
                updated_on=current_time,
            )
        )
        self.session.commit()

    def update_org_draft(self, current_draft, organization, username):
        current_draft.name = organization.name
        current_draft.org_id = organization.org_id
        current_draft.type = organization.org_type
        current_draft.description = organization.description
        current_draft.short_description = organization.short_description
        current_draft.url = organization.url
        current_draft.contacts = organization.contacts
        current_draft.assets = organization.assets
        current_draft.ipfs_hash = organization.ipfs_hash
        current_draft.updated_by = username
        current_draft.updated_on = datetime.utcnow()
        self.session.commit()

    def get_latest_org_from_org_id(self, org_uuid):
        query = self.session.query(OrganizationReviewWorkflow)\
            .join(Organization, OrganizationReviewWorkflow.org_row_id == Organization.row_id)\
            .filter(Organization.org_uuid == org_uuid)
        return query.all()

    def get_current_drafts(self, organization):
        current_drafts = self.session.query(Organization) \
            .join(OrganizationReviewWorkflow, Organization.row_id == OrganizationReviewWorkflow.org_row_id) \
            .filter(Organization.org_uuid == organization.org_uuid) \
            .filter(OrganizationReviewWorkflow.status == "DRAFT").all()
        return current_drafts

    def remove_pending_approval_for_org(self, organization):
        pending_approval_org = self.session.query(Organization) \
            .join(OrganizationReviewWorkflow, Organization.row_id == OrganizationReviewWorkflow.org_row_id) \
            .filter(Organization.org_uuid == organization.org_uuid) \
            .filter(OrganizationReviewWorkflow.status == "PENDING_APPROVAL").all()
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
                    ipfs_hash=org.ipfs_hash
                ))

            self.add_all_items(org_history)
            self.session.commit()
            self.session.query(Organization).filter(Organization.row_id.in_(row_ids))\
                .delete(synchronize_session='fetch')
            self.session.commit()
            x = 0
        self.add_all_items(items)
