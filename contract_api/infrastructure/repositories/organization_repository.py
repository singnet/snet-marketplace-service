from sqlalchemy import select

from contract_api.domain.factory.organization_factory import OrganizationFactory
from contract_api.domain.models.org_group import OrgGroupDomain
from contract_api.domain.models.organization import OrganizationDomain
from contract_api.infrastructure.models import OrgGroup, Organization, Service
from contract_api.infrastructure.repositories.base_repository import BaseRepository


class OrganizationRepository(BaseRepository):
    def get_groups(self, org_id: str, group_id: str = None) -> list[OrgGroupDomain]:
        query = select(
            OrgGroup
        ).where(
            OrgGroup.org_id == org_id
        )

        if group_id is not None:
            query = query.where(OrgGroup.group_id == group_id)

        result = self.session.execute(query)
        groups_db = result.scalars().all()

        return OrganizationFactory.org_groups_from_db_model(groups_db)

    def get_organizations_with_curated_services(self) -> list[OrganizationDomain]:
        query = select(
            Organization
        ).join(
            Service, Organization.org_id == Service.org_id
        ).where(
            Service.is_curated == True
        ).distinct()

        result = self.session.execute(query)
        organizations_db = result.scalars().all()

        return OrganizationFactory.orgs_from_db_model(organizations_db)
