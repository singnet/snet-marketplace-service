from common.ipfs_util import IPFSUtil
from common.utils import json_to_file
from registry.config import IPFS_URL
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self.org_repo = OrganizationRepository()

    def add_organization_draft(self, payload, username):
        """
            TODO: add member owner validation
        """
        organization = OrganizationFactory.parse_raw_organization(payload)
        organization.setup_id()
        if organization.validate_draft():
            raise Exception(f"Validation failed for the Organization {organization.to_dict()}")
        self.org_repo.draft_update_org(organization, username)
        self.org_repo.remove_pending_approval_for_org(organization)
        return organization.to_dict()

    def submit_org_for_approval(self):
        pass

    def publish_org_ipfs(self, org_uuid):
        organization = self.org_repo.get_approved_org_from_org_uuid(org_uuid)
        if len(organization) == 0:
            raise Exception(f"Organization not found with uuid {org_uuid}")
        metadata = organization[0].to_metadata()
        filename = f"{org_uuid}_org_metadata.json"
        json_to_file(metadata, filename)
        ipfs_utils = IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        metadata_ipfs_hash = ipfs_utils.write_file_in_ipfs(filename)
        organization.set_metadata_ipfs_hash(metadata_ipfs_hash)
        return organization

    def get_organizations_for_user(self, username):
        organization = self.org_repo.get_organization_for_user(username)
        return organization

    def get_organization(self):
        organizations = self.org_repo.get_published_organization()
        return organizations
