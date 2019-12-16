from datetime import datetime

from registry.infrastructure.models.models import Group
from registry.infrastructure.models.models import Organization, WorkFlow
from registry.infrastructure.repositories.base_repository import BaseRepository


class OrganizationRepository(BaseRepository):

    def persist_org_draft(self, organization, username):
        org_id = organization.org_id
        organization_item = Organization(
            name=organization.name,
            id=organization.org_id,
            type=organization.org_type,
            description=organization.description,
            short_description=organization.short_description,
            url=organization.url,
            contacts=organization.contacts,
            assets=organization.assets
        )
        self.add_item(organization_item)
        org_row_id = organization_item.row_id

        current_time = datetime.utcnow()
        items = [
            WorkFlow(
                org_row_id=org_row_id,
                status="DRAFT",
                created_by=username,
                updated_by=username,
                create_on=current_time,
                updated_on=current_time,
            )
        ]
        for group in organization.groups:
            items.append(
                Group(
                    id=group.group_id,
                    name=group.name,
                    org_id=org_id,
                    payment_address=group.payment_address,
                    payment_config=group.payment_config
                )
            )
        self.add_all_items(items)

    def get_org_latest_from_org_id(self, org_id):
        query = self.session.query(WorkFlow)\
            .join(Organization, WorkFlow.org_row_id == Organization.row_id).filter(Organization.id == org_id)
        return query.all()
