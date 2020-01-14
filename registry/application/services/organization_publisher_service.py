from common.boto_utils import BotoUtils
from common.exceptions import OrganizationNotFound
from registry.application.access import Action, secured
from registry.config import REGION_NAME
from registry.constants import OrganizationStatus
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository

org_repo = OrganizationRepository()


class OrganizationService(object):
    # __metaclass__ = OrganizationAccessControl

    def __init__(self, org_uuid, username):

        self.boto_utils = BotoUtils(region_name=REGION_NAME)
        self.org_uuid = org_uuid
        self.username = username

    """
    We have three actions

    DRAFT add_organization_draft
    SUBMIT submit_org_for_approval
    PUBLISH publish_org_to_ipfs,save_transaction_hash_for_publish_org



    and organization STATES
    DRAFT
    PENDING_APPROVAL
    APPROVED
    PUBLISH_IN_PROGRESS
    PUBLISHED
    PUBLISH_UNAPPROVED

    based on action organization will changes states
    """

    """
    Whenever new draft will come,
    move APPROVAL_PENDING, APPROVED to the history table
    """

    def add_organization_draft(self, payload):
        """
            TODO: add member owner validation
        """
        organization = OrganizationFactory.parse_raw_organization(payload)
        organization.add_owner(self.username)
        if not organization.is_valid_draft():
            raise Exception(f"Validation failed for the Organization {organization.to_dict()}")
        if self.is_on_boarding_approved():
            org_repo.move_non_published_org_to_history(organization.org_uuid)
            org_repo.add_org_with_status(organization, OrganizationStatus.APPROVED.value, self.username)
        else:
            org_repo.draft_update_org(organization, self.username)
            org_repo.move_non_published_org_to_history(organization.org_uuid)
        return organization.to_dict()

    def submit_org_for_approval(self, payload):
        organization = OrganizationFactory.parse_raw_organization(payload)
        organization.add_owner(self.username)
        if not organization.is_valid_draft():
            raise Exception(f"Validation failed for the Organization {organization.to_dict()}")
        if self.is_on_boarding_approved():
            org_repo.move_non_published_org_to_history(organization.org_uuid)
            org_repo.add_org_with_status(organization, OrganizationStatus.APPROVED.value, self.username)
        else:
            org_repo.draft_update_org(organization, self.username)
            org_repo.move_non_published_org_to_history(organization.org_uuid)
            org_repo.change_org_status(organization.org_uuid, OrganizationStatus.DRAFT.value,
                                       OrganizationStatus.APPROVAL_PENDING.value, self.username)
        return organization.to_dict()

    def is_on_boarding_approved(self):

        published_orgs = org_repo.get_published_org_for_user(self.username)
        latest_orgs = org_repo.get_org_status(self.org_uuid)

        if len(published_orgs) != 0:
            return False
        if len(latest_orgs) == 0:
            return False

        if latest_orgs[0].status == "APPROVED":
            return True

        return False

    def publish_org_to_ipfs(self):
        orgs = org_repo.get_approved_org(self.org_uuid)
        if len(orgs) == 0:
            raise Exception(f"Organization not found with uuid {self.org_uuid}")
        organization = orgs[0]
        organization.publish_to_ipfs()
        org_repo.persist_metadata_and_assets_ipfs_hash(organization)
        return organization.to_dict()

    def save_transaction_hash_for_publish_org(self, transaction_hash, wallet_address):
        orgs = org_repo.get_approved_org(self.org_uuid)
        if len(orgs) == 0:
            raise OrganizationNotFound(f"Organization not found with uuid {self.org_uuid}")
        organization = orgs[0]
        org_repo.move_org_to_history_with_status(organization.org_uuid, OrganizationStatus.APPROVED.value)
        org_repo.add_org_with_status(organization, OrganizationStatus.PUBLISH_IN_PROGRESS.value, self.username,
                                     transaction_hash=transaction_hash, wallet_address=wallet_address)
        return "OK"

    def get_organizations_for_user(self):
        organizations = org_repo.get_latest_organization(self.username)
        response = []
        for org_data in organizations:
            response.append(org_data.to_dict())
        return response

    def get_organization(self):
        organizations = org_repo.get_published_organization()
        return organizations

    def add_group(self, payload):
        groups = OrganizationFactory().parse_raw_list_groups(payload)
        for group in groups:
            group.setup_id()
            if not group.validate_draft():
                raise Exception(f"validation failed for the group {group.to_dict()}")
        org_repo.add_group(groups, self.org_uuid, self.username)
        return "OK"

    @secured(action=Action.READ)
    def get_role_for_org_member(self):
        organizations = org_repo.get_org_using_org_id(self.org_uuid)
        members = set()
        for organization in organizations:
            members.add(organization.members)

        response = [member.role_response() for member in members]
        return response
