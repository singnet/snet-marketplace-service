from sqlalchemy import select, delete, update

from contract_api.domain.factory.organization_factory import OrganizationFactory
from contract_api.domain.models.org_group import OrgGroupDomain, NewOrgGroupDomain
from contract_api.domain.models.organization import OrganizationDomain, NewOrganizationDomain
from contract_api.infrastructure.models import OrgGroup, Organization, Service, Members
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

    def get_organization(self, org_id: str) -> OrganizationDomain:
        query = select(
            Organization
        ).where(
            Organization.org_id == org_id
        ).limit(1)

        result = self.session.execute(query)
        organization_db = result.scalar_one_or_none()

        return OrganizationFactory.organization_from_db_model(organization_db)

    def delete_organization(self, org_id: str) -> None:
        query = delete(
            Organization
        ).where(
            Organization.org_id == org_id
        )
        self.session.execute(query)

        self.session.commit()

    def upsert_organization(self, organization: NewOrganizationDomain) -> None:
        query = select(
            Organization
        ).where(
            Organization.org_id == organization.org_id
        ).limit(1)

        result = self.session.execute(query)
        organization_db = result.scalar_one_or_none()

        if organization_db:
            query = update(
                Organization
            ).where(
                Organization.org_id == organization.org_id
            ).values(
                organization_name = organization.organization_name,
                owner_address = organization.owner_address,
                org_metadata_uri = organization.org_metadata_uri,
                org_assets_url = organization.org_assets_url,
                is_curated = organization.is_curated,
                description = organization.description,
                assets_hash = organization.assets_hash,
                contacts = organization.contacts
            )

            self.session.execute(query)
        else:
            self.session.add(
                Organization(
                    org_id=organization.org_id,
                    organization_name = organization.organization_name,
                    owner_address = organization.owner_address,
                    org_metadata_uri = organization.org_metadata_uri,
                    org_assets_url = organization.org_assets_url,
                    is_curated = organization.is_curated,
                    description = organization.description,
                    assets_hash = organization.assets_hash,
                    contacts = organization.contacts
                )
            )

    def delete_org_groups(self, org_id: str) -> None:
        query = delete(
            OrgGroup
        ).where(
            OrgGroup.org_id == org_id
        )
        self.session.execute(query)

    def create_org_groups(
            self,
            groups: list[NewOrgGroupDomain]
    ) -> None:
        for group in groups:
            self.session.add(
                OrgGroup(
                    org_id=group.org_id,
                    group_id=group.group_id,
                    group_name=group.group_name,
                    payment=group.payment
                )
            )



