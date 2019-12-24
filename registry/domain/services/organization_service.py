import requests

from urllib.parse import urlparse
from common.boto_utils import BotoUtils
from registry.config import IPFS_URL, METADATA_FILE_PATH, REGION_NAME, ASSET_DIR
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository


class OrganizationService:
    def __init__(self):
        self.org_repo = OrganizationRepository()
        self.boto_utils = BotoUtils(region_name=REGION_NAME)

    def add_organization_draft(self, payload, username):
        """
            TODO: add member owner validation
        """
        organization = OrganizationFactory.parse_raw_organization(payload)
        if not organization.is_valid_draft():
            raise Exception(f"Validation failed for the Organization {organization.to_dict()}")
        self.org_repo.draft_update_org(organization, username)
        self.org_repo.export_org_with_status(organization, "PENDING_APPROVAL")
        return organization.to_dict()

    def submit_org_for_approval(self, org_uuid, username):
        self.org_repo.change_org_status(org_uuid, "DRAFT", "APPROVAL_PENDING", username)
        return "OK"

    def publish_org(self, org_uuid, username):
        orgs = self.org_repo.get_approved_org(org_uuid)
        if len(orgs) == 0:
            raise Exception(f"Organization not found with uuid {org_uuid}")
        organization = orgs[0]
        organization.publish_org()
        self.org_repo.export_org_with_status(organization, "APPROVED")
        self.org_repo.add_org_with_status(organization, "PUBLISH_IN_PROGRESS", username)
        return organization.to_dict()

    def get_organizations_for_user(self, username):
        organization = self.org_repo.get_organization_for_user(username)
        return organization

    def get_organization(self):
        organizations = self.org_repo.get_published_organization()
        return organizations
