from uuid import uuid4

from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self.org_repo = OrganizationRepository()

    def add_organization_draft(self, payload, username):
        organization = OrganizationFactory.parse_raw_organization(payload)
        organization.setup_id()
        self.org_repo.draft_update_org(organization, username)
        self.org_repo.remove_pending_approval_for_org(organization)
