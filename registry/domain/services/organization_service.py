from common.boto_utils import BotoUtils
from registry.config import IPFS_URL, METADATA_FILE_PATH, REGION_NAME, ASSET_DIR
from registry.constants import OrganizationStatus
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self.org_repo = OrganizationRepository()
        self.boto_utils = BotoUtils(region_name=REGION_NAME)

    """
    Whenever new draft will come,
    move APPROVAL_PENDING, APPROVED to the history table
    """

    def add_organization_draft(self, payload, username):
        """
            TODO: add member owner validation
        """
        organization = OrganizationFactory.parse_raw_organization(payload)
        if not organization.is_valid_draft():
            raise Exception(f"Validation failed for the Organization {organization.to_dict()}")
        self.org_repo.draft_update_org(organization, username)
        self.org_repo.move_non_published_org_to_history(organization.org_uuid)
        return organization.to_dict()

    def submit_org_for_approval(self, org_uuid, username):
        self.org_repo.change_org_status(org_uuid, OrganizationStatus.DRAFT.value,
                                        OrganizationStatus.APPROVAL_PENDING.value, username)
        return "OK"

    def publish_org_to_ipfs(self, org_uuid, username):
        orgs = self.org_repo.get_approved_org(org_uuid)
        if len(orgs) == 0:
            raise Exception(f"Organization not found with uuid {org_uuid}")
        organization = orgs[0]
        organization.publish_to_ipfs()
        self.org_repo.persist_ipfs_hash(organization)
        return organization.to_dict()

    def save_transaction(self, org_uuid, transaction_hash, wallet_address, username):
        orgs = self.org_repo.get_approved_org(org_uuid)
        if len(orgs) == 0:
            raise Exception(f"Organization not found with uuid {org_uuid}")
        organization = orgs[0]
        self.org_repo.move_org_to_history_with_status(organization.org_uuid, OrganizationStatus.APPROVED.value)
        self.org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISH_IN_PROGRESS.value, username,
                                          transaction_hash=transaction_hash, wallet_address=wallet_address)
        return "OK"

    def get_organizations_for_user(self, username):
        organization = self.org_repo.get_organization_for_user(username)
        return organization

    def get_organization(self):
        organizations = self.org_repo.get_published_organization()
        return organizations

    def add_group(self, payload, org_uuid, username):
        groups = OrganizationFactory().parse_raw_list_groups(payload)
        for group in groups:
            group.setup_id()
            if not group.validate_draft():
                raise Exception(f"validation failed for the group {group.to_dict()}")
        self.org_repo.add_group(groups, org_uuid, username)
        return "OK"
