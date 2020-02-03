from registry.constants import OrganizationStatus
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.models.organization import OrganizationState
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

org_repo = OrganizationPublisherRepository()


class OrganizationPublisherService:
    def __init__(self, org_uuid, username):
        self.org_uuid = org_uuid
        self.username = username

    def get_all_org_for_user(self):
        organizations = org_repo.get_org_for_user(username=self.username)
        return [org.to_dict() for org in organizations]

    def add_organization_draft(self, payload):
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        org_repo.store_organization(organization, self.username, OrganizationStatus.DRAFT.value)
        return "OK"

    def submit_org_for_approval(self, payload):
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        org_repo.store_organization(organization, self.username, OrganizationStatus.APPROVAL_PENDING.value)
        return "OK"

    def publish_org_to_ipfs(self):
        organization = org_repo.get_org(self.org_uuid)
        organization.publish_to_ipfs()
        org_repo.store_ipfs_hash(organization, self.username)
        return organization.to_dict()

    def save_transaction_hash_for_publish_org(self, payload):
        transaction_hash = payload["transaction_hash"]
        user_address = payload["user_address"]
        org_repo.persist_publish_org_transaction_hash(self.org_uuid, transaction_hash, user_address, self.username)
        return "OK"
