from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.item_pipeline import ItemPipeline
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class OrganizationService:

    def add_organization_draft(self, payload, username):
        organization = OrganizationFactory.parse_raw_organization(payload)
        OrganizationRepository().persist_org_draft(organization, username)
