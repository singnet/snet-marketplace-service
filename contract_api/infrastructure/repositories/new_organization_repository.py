from typing import Optional

from sqlalchemy import select, delete, update

from contract_api.domain.factory.organization_factory import OrganizationFactory
from contract_api.domain.models.org_group import OrgGroupDomain, NewOrgGroupDomain
from contract_api.domain.models.organization import OrganizationDomain, NewOrganizationDomain
from contract_api.infrastructure.models import OrgGroup, Organization, Service
from contract_api.infrastructure.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class NewOrganizationRepository(BaseRepository):
    def get_groups(
        self, session: Session, org_id: str, group_id: str | None = None
    ) -> list[OrgGroupDomain]:
        query = select(OrgGroup).where(OrgGroup.org_id == org_id)

        if group_id is not None:
            query = query.where(OrgGroup.group_id == group_id)

        result = session.execute(query)
        groups_db = result.scalars().all()

        return OrganizationFactory.org_groups_from_db_model(groups_db)

    def get_organizations_with_curated_services(self, session) -> list[OrganizationDomain]:
        query = (
            select(Organization)
            .join(Service, Organization.org_id == Service.org_id)
            .where(Service.is_curated == True)
            .distinct()
        )

        result = session.execute(query)
        organizations_db = result.scalars().all()

        return OrganizationFactory.orgs_from_db_model(organizations_db)

    def get_organization(self, session: Session, org_id: str) -> Optional[OrganizationDomain]:
        query = select(Organization).where(Organization.org_id == org_id).limit(1)

        result = session.execute(query)
        organization_db = result.scalar_one_or_none()

        if organization_db is None:
            return None

        return OrganizationFactory.organization_from_db_model(organization_db)

    @BaseRepository.write_ops
    def delete_organization(self, session: Session, org_id: str) -> None:
        query = delete(Organization).where(Organization.org_id == org_id)
        session.execute(query)

        session.commit()

    def upsert_organization(self, session: Session, organization: NewOrganizationDomain) -> None:
        query = select(Organization).where(Organization.org_id == organization.org_id).limit(1)

        result = session.execute(query)
        organization_db = result.scalar_one_or_none()

        if organization_db is not None:
            update_query = (
                update(Organization)
                .where(Organization.org_id == organization.org_id)
                .values(
                    organization_name=organization.organization_name,
                    owner_address=organization.owner_address,
                    org_metadata_uri=organization.org_metadata_uri,
                    org_assets_url=organization.org_assets_url,
                    is_curated=organization.is_curated,
                    description=organization.description,
                    assets_hash=organization.assets_hash,
                    contacts=organization.contacts,
                )
            )

            session.execute(update_query)
        else:
            session.add(
                Organization(
                    org_id=organization.org_id,
                    organization_name=organization.organization_name,
                    owner_address=organization.owner_address,
                    org_metadata_uri=organization.org_metadata_uri,
                    org_assets_url=organization.org_assets_url,
                    is_curated=organization.is_curated,
                    description=organization.description,
                    assets_hash=organization.assets_hash,
                    contacts=organization.contacts,
                )
            )

    def delete_org_groups(self, session: Session, org_id: str) -> None:
        query = delete(OrgGroup).where(OrgGroup.org_id == org_id)
        session.execute(query)

    def create_org_groups(self, session: Session, groups: list[NewOrgGroupDomain]) -> None:
        for group in groups:
            session.add(
                OrgGroup(
                    org_id=group.org_id,
                    group_id=group.group_id,
                    group_name=group.group_name,
                    payment=group.payment,
                )
            )
