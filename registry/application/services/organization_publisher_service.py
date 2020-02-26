import json
from datetime import datetime

from web3 import Web3

from common.boto_utils import BotoUtils
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from registry.config import NOTIFICATION_ARN, PUBLISHER_PORTAL_DAPP_URL, REGION_NAME
from registry.constants import OrganizationStatus, OrganizationMemberStatus, Role
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

org_repo = OrganizationPublisherRepository()

logger = get_logger(__name__)


class OrganizationPublisherService:
    def __init__(self, org_uuid, username):
        self.org_uuid = org_uuid
        self.username = username
        self.boto_utils = BotoUtils(region_name=REGION_NAME)

    def get_for_admin(self, params):
        status = params.get("status", None)
        organizations = org_repo.get_org(status)
        return [org.to_response() for org in organizations]

    def get_all_org_for_user(self):
        logger.info(f"get organization for user: {self.username}")
        organizations = org_repo.get_org_for_user(username=self.username)
        return [org.to_response() for org in organizations]

    def get_groups_for_org(self):
        logger.info(f"get groups for org_uuid: {self.org_uuid}")
        groups = org_repo.get_groups_for_org(self.org_uuid)
        return {
            "org_uuid": self.org_uuid,
            "groups": [group.to_response() for group in groups]
        }

    def create_organization(self, payload):
        logger.info(f"create organization for user: {self.username}")
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        organization.setup_id()
        logger.info(f"assigned org_uuid : {organization.uuid}")
        org_repo.add_organization(organization, self.username, OrganizationStatus.ONBOARDING.value)
        return "OK"

    def save_organization_draft(self, payload):
        logger.info(f"edit organization for user: {self.username} org_uuid: {self.org_uuid}")
        updated_organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        current_organization = org_repo.get_org_for_org_uuid(self.org_uuid)
        self._archive_current_organization(current_organization)

        if current_organization.is_minor(updated_organization):
            org_repo.update_organization(updated_organization, self.username, OrganizationStatus.DRAFT.value)
        else:
            raise MethodNotImplemented()
        return "OK"

    def _archive_current_organization(self, organization):
        if organization.get_status() == OrganizationStatus.PUBLISHED.value:
            org_repo.add_organization_archive(organization)

    def submit_organization_for_approval(self, payload):
        logger.info(f"submit for approval organization org_uuid: {self.org_uuid}")
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        if not organization.is_valid():
            raise Exception("Invalid org metadata")
        org_repo.store_organization(organization, self.username, OrganizationStatus.APPROVED.value)
        return "OK"

    def publish_org_to_ipfs(self):
        logger.info(f"publish organization to ipfs org_uuid: {self.org_uuid}")
        organization = org_repo.get_org_for_org_uuid(self.org_uuid)
        organization.publish_to_ipfs()
        org_repo.store_ipfs_hash(organization, self.username)
        return organization.to_response()

    def save_transaction_hash_for_publish_org(self, payload):
        transaction_hash = payload["transaction_hash"]
        user_address = payload["wallet_address"]
        logger.info(f"save transaction hash for publish organization org_uuid: {self.org_uuid} "
                    f"transaction_hash: {transaction_hash} user_address: {user_address}")
        org_repo.persist_publish_org_transaction_hash(self.org_uuid, transaction_hash, user_address, self.username)
        return "OK"

    def get_all_member(self, status, role, pagination_details):
        offset = pagination_details.get("offset", None)
        limit = pagination_details.get("limit", None)
        sort = pagination_details.get("sort", None)
        org_members_list = org_repo.get_org_member(org_uuid=self.org_uuid, status=status, role=role)
        return [member.to_response() for member in org_members_list]

    def get_member(self, member_username):
        members = org_repo.get_org_member(username=member_username, org_uuid=self.org_uuid)
        if len(members) == 0:
            logger.info(f"No member {member_username} for the organization {self.org_uuid}")
            return []
        return [member.to_response() for member in members]

    def verify_invite(self, invite_code):
        logger.info(f"verify member invite_code: {invite_code} username: {self.username}")
        if org_repo.org_member_verify(self.username, invite_code):
            return "OK"
        return "NOT_FOUND"

    def delete_members(self, org_members):
        logger.info(f"user: {self.username} requested to delete members: {org_members} of org_uuid: {self.org_uuid}")
        org_member_list = OrganizationFactory.org_member_domain_entity_from_payload_list(org_members, self.org_uuid)
        org_repo.delete_members(org_member_list)
        return "OK"

    def publish_members(self, transaction_hash, org_members):
        logger.info(f"user: {self.username} published members: {org_members} with transaction_hash: {transaction_hash}")
        org_member = OrganizationFactory.org_member_domain_entity_from_payload_list(org_members, self.org_uuid)
        org_repo.persist_publish_org_member_transaction_hash(org_member, transaction_hash, self.org_uuid)
        return "OK"

    def register_member(self, invite_code, wallet_address):
        logger.info(f"register user: {self.username} with invite_code: {invite_code}")
        if Web3.isAddress(wallet_address):
            org_repo.update_org_member(self.username, wallet_address, invite_code)
        else:
            raise Exception("Invalid wallet address")
        return "OK"

    def invite_members(self, members_payload):
        current_time = datetime.utcnow()
        requested_invite_member_list = OrganizationFactory.org_member_domain_entity_from_payload_list(members_payload,
                                                                                                      self.org_uuid)
        current_org_member = org_repo.get_org_member(org_uuid=self.org_uuid)
        current_org_member_username_list = [member.username for member in current_org_member]
        eligible_invite_member_list = [member for member in requested_invite_member_list
                                       if member.username not in current_org_member_username_list]
        for org_member in eligible_invite_member_list:
            org_member.generate_invite_code()
            org_member.set_status(OrganizationMemberStatus.PENDING.value)
            org_member.set_role(Role.MEMBER.value)
            org_member.set_invited_on(current_time)
            org_member.set_updated_on(current_time)

        organization = org_repo.get_org_for_org_uuid(self.org_uuid)
        org_name = organization.name
        self._send_email_notification_for_inviting_organization_member(eligible_invite_member_list, org_name)
        org_repo.add_member(eligible_invite_member_list)

        failed_invitation = [member.username for member in requested_invite_member_list
                             if member.username in current_org_member_username_list]
        return {"member": [member.to_response() for member in eligible_invite_member_list],
                "failed_invitation": failed_invitation}

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
        return f"<html><head></head><body><div><p>Hello,</p><p>Organization {org_name} has sent you membership invite. " \
               f"Your invite code is <strong>{invite_code}</strong>.</p><br/><p>Please click on the link below to " \
               f"accept the invitation.</p><p>{PUBLISHER_PORTAL_DAPP_URL}</p><br/><br/><p>" \
               "<em>Please do not reply to the email for any enquiries for any queries please email at " \
               "cs-marketplace@singularitynet.io.</em></p><p>Warmest regards, <br />SingularityNET Marketplace " \
               "Team</p></div></body></html>"

    @staticmethod
    def _get_org_member_notification_subject(org_name):
        return f"Membership Invitation from  Organization {org_name}"
