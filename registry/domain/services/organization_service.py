import common.ipfs_util as ipfs_util
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
        if not organization.is_valid_draft():
            raise Exception(f"Validation failed for the Organization {organization.to_dict()}")
        self.org_repo.draft_update_org(organization, username)
        self.org_repo.export_org_with_status(organization, "PENDING_APPROVAL")
        return organization.to_dict()

    def submit_org_for_approval(self, org_uuid):
        pass

    def publish_org(self, org_uuid, username):
        orgs = self.org_repo.get_approved_org(org_uuid)
        if len(orgs) == 0:
            raise Exception(f"Organization not found with uuid {org_uuid}")
        organization = orgs[0]
        metadata = organization.to_metadata()
        metadata_ipfs_hash = self.publish_org_to_ipfs(metadata, org_uuid)
        organization.set_metadata_ipfs_hash(metadata_ipfs_hash)
        self.org_repo.export_org_with_status(organization, "APPROVED")
        self.org_repo.add_org_with_status(organization, "PUBLISH_IN_PROGRESS", username)
        return organization.to_dict()

    def publish_org_to_ipfs(self, metadata, org_uuid):
        filename = f"{org_uuid}_org_metadata.json"
        json_to_file(metadata, filename)
        ipfs_utils = ipfs_util.IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
        metadata_ipfs_hash = ipfs_utils.write_file_in_ipfs(filename)
        return metadata_ipfs_hash

    def get_organizations_for_user(self, username):
        organization = self.org_repo.get_organization_for_user(username)
        return organization

    def get_organization(self):
        organizations = self.org_repo.get_published_organization()
        return organizations
