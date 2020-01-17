import json
from web3 import Web3

from common.boto_utils import BotoUtils
from common.exceptions import OrganizationNotFound
from registry.application.access import secured
from common.logger import get_logger
from registry.config import REGION_NAME, NOTIFICATION_ARN
from registry.constants import OrganizationStatus, Role, Action, OrganizationMemberStatus
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository

org_repo = OrganizationRepository()
logger = get_logger(__name__)


class OrganizationService(object):

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

    def get_member(self, member_username):
        member = org_repo.get_org_member_details_from_username(member_username, self.org_uuid)
        if member is None:
            logger.info(f"No member {member_username} for the organization {self.org_uuid}")
            return []
        return [member.to_dict()]

    def get_all_members(self, org_uuid, status, pagination_details):
        offset = pagination_details.get("offset", None)
        limit = pagination_details.get("limit", None)
        sort = pagination_details.get("sort", None)
        org_members_list = org_repo.get_members_for_given_org_and_status(org_uuid, status)
        return [member.to_dict() for member in org_members_list]

    def publish_members(self, transaction_hash, org_members):
        org_member_list = OrganizationFactory.org_member_from_dict_list(org_members, self.org_uuid)
        org_repo.persist_transaction_hash(org_member_list, transaction_hash)
        return "OK"

    def invite_members(self, org_members):
        org_member_list = OrganizationFactory.org_member_from_dict_list(org_members, self.org_uuid)
        for org_member in org_member_list:
            org_member.generate_invite_code()
        org_data = org_repo.get_latest_org_from_org_uuid(org_uuid=self.org_uuid)
        if len(org_data) > 0:
            org_name = org_data[0].Organization.name
        else:
            raise Exception("Unable to find organization.")
        self._send_invitation(org_member_list, org_name)
        org_repo.add_member(org_member_list, status=OrganizationMemberStatus.PENDING.value)

    def _send_invitation(self, org_member_list, org_name):
        self._send_email_notification_for_inviting_organization_member(org_member_list, org_name)

    def verify_invite(self, invite_code):
        if org_repo.org_member_verify(self.username, invite_code):
            return "OK"
        return "NOT_FOUND"

    def delete_members(self, org_members):
        org_member_list = OrganizationFactory.org_member_from_dict_list(org_members, self.org_uuid)
        org_repo.delete_members(org_member_list)

    def register_member(self, wallet_address):
        if Web3.isAddress(wallet_address):
            org_repo.update_org_member(self.org_uuid, self.username, wallet_address)
        else:
            raise Exception("Invalid wallet address")
        return "OK"

    def _send_email_notification_for_inviting_organization_member(self, org_members_list, org_name):
        for org_member in org_members_list:
            recipient = org_member.username
            org_member_notification_subject = self._get_org_member_notification_subject(org_name)
            org_member_notification_message = self._get_org_member_notification_message(org_member.invite_code,
                                                                                        org_name)
            send_notification_payload = {"body": json.dumps({
                "message": org_member_notification_message,
                "subject": org_member_notification_subject,
                "notification_type": "support",
                "recipient": recipient})}
            self.boto_utils.invoke_lambda(lambda_function_arn=NOTIFICATION_ARN, invocation_type="RequestResponse",
                                          payload=json.dumps(send_notification_payload))
            logger.info(f"Org Membership Invite sent to {recipient}")

    @staticmethod
    def _get_org_member_notification_message(invite_code, org_name):
        return f"Organization {org_name} has sent you membership invite. Your invite code is {invite_code}."

    @staticmethod
    def _get_org_member_notification_subject(org_name):
        return f"Membership Invitation from  Organization {org_name}"

    def get_organizations_transaction_data(self):
        orgs_transaction_data = self.org_repo.get_all_organization_transaction_data()
        for org_transaction_data in orgs_transaction_data:
            transaction_receipt = self.blockchain_utils.get_transaction_receipt_from_blockchain(
                transaction_hash=orgs_transaction_data["transaction_hash"])
            if transaction_receipt is not None:
                status = OrganizationStatus.PUBLISHED.value if transaction_receipt.status == 1 else OrganizationStatus.FAILED.value
                self.org_repo.update_organization_review_workflow_status(orgs_transaction_data["row_id"], status)


class OrganizationMemberService:

    @staticmethod
    def compute_org_uuid_for_given_username_and_invite_code(username, invite_code):
        org_member_data = org_repo.get_org_member_details_from_username_and_invite_code(username, invite_code)
        if org_member_data is not None:
            return org_member_data["org_uuid"]
        raise Exception(f"Invite not found for member {username} with given invitation code")
