from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.models import Organization, OrganizationMember
from registry.infrastructure.repositories.base_repository import BaseRepository


class OrganizationPublisherRepository(BaseRepository):

    def get_org_for_user(self, username):
        organizations = self.session.query(Organization)\
            .join(OrganizationMember, Organization.uuid == OrganizationMember.org_uuid)\
            .filter(OrganizationMember.username == username).all()
        organizations_domain_entity = OrganizationFactory.org_domain_entity_from_repo_model_list(organizations)
        self.session.commit()
        return organizations_domain_entity

