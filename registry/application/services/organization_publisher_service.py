import json
from datetime import datetime

from web3 import Web3

from common import utils
from common.boto_utils import BotoUtils
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from common.utils import Utils
import registry.config
from registry.constants import EnvironmentType, ORG_STATUS_LIST, ORG_TYPE_VERIFICATION_TYPE_MAPPING, \
    OrganizationActions, OrganizationIDAvailabilityStatus, OrganizationMemberStatus, OrganizationStatus, \
    OrganizationType, Role
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.models.organization import Organization
from registry.domain.services.registry_blockchain_util import RegistryBlockChainUtil
from registry.exceptions import InvalidOrganizationStateException, BadRequestException
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.mail_templates import \
    get_notification_mail_template_for_service_provider_when_org_is_submitted_for_onboarding, \
    get_owner_mail_for_org_rejected, get_owner_mail_for_org_changes_requested, get_owner_mail_for_org_approved
from registry.mail_templates import get_org_member_invite_mail, get_org_approval_mail

org_repo = OrganizationPublisherRepository()

logger = get_logger(__name__)
ORG_APPROVE_SUBJECT = "Organization  {} Approved "
ORG_APPROVE_MESSAGE = "You organization  {} has been approved"


class OrganizationPublisherService:
    def __init__(self, org_uuid, username):
        self.org_uuid = org_uuid
        self.username = username
        self.boto_utils = BotoUtils(region_name=registry.config.REGION_NAME)

    def get_approval_pending_organizations(self, limit, type=None):
        status = OrganizationStatus.ONBOARDING.value
        organizations = org_repo.get_organizations(status, limit, type)
        return [org.to_response() for org in organizations]

    def get_all_org_for_user(self):
        logger.info(f"get organization for user: {self.username}")
        organizations = org_repo.get_all_orgs_for_user(username=self.username)
        return [org.to_response() for org in organizations]

    def get_all_org_id(self):
        organizations = org_repo.get_organizations()
        return [org.id for org in organizations]

    def get_org_id_availability_status(self, org_id):
        org_id_list = self.get_all_org_id()

        if org_id in org_id_list:
            return OrganizationIDAvailabilityStatus.UNAVAILABLE.value
        if RegistryBlockChainUtil(EnvironmentType.MAIN.value).is_org_published(org_id):
            return OrganizationIDAvailabilityStatus.UNAVAILABLE.value
        return OrganizationIDAvailabilityStatus.AVAILABLE.value

    def get_groups_for_org(self):
        logger.info(f"get groups for org_uuid: {self.org_uuid}")
        groups = org_repo.get_groups_for_org(self.org_uuid)
        return {
            "org_uuid": self.org_uuid,
            "groups": [group.to_response() for group in groups]
        }

    def create_organization(self, payload):
        logger.info(f"create organization for user: {self.username}, payload: {payload}")
        organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        organization.setup_id()
        logger.info(f"assigned org_uuid : {organization.uuid}")
        org_ids = self.get_all_org_id()
        if organization.id in org_ids:
            raise Exception("Org_id already exists")
        updated_state = Organization.next_state(None, None, OrganizationActions.CREATE.value)
        org_repo.add_organization(organization, self.username, updated_state)
        organization = org_repo.get_organization(org_id=organization.id)
        return organization.to_response()

    def update_organization(self, payload, action):
        logger.info(f"update organization for user: {self.username} org_uuid: {self.org_uuid} action: {action}")
        updated_organization = OrganizationFactory.org_domain_entity_from_payload(payload)
        current_organization = org_repo.get_organization(org_uuid=self.org_uuid)
        self._archive_current_organization(current_organization)
        updated_state = Organization.next_state(current_organization, updated_organization, action)
        org_repo.update_organization(updated_organization, self.username, updated_state)
        return "OK"

    def notify_user_on_start_of_onboarding_process(self, org_id, recipients):
        if not recipients:
            logger.info(f"Unable to find recipients for organization with org_id {org_id}")
            return
        mail_template = get_notification_mail_template_for_service_provider_when_org_is_submitted_for_onboarding(org_id)
        for recipient in recipients:
            send_notification_payload = {"body": json.dumps({
                "message": mail_template["body"],
                "subject": mail_template["subject"],
                "notification_type": "support",
                "recipient": recipient})}
            self.boto_utils.invoke_lambda(lambda_function_arn=registry.config.NOTIFICATION_ARN, invocation_type="RequestResponse",
                                          payload=json.dumps(send_notification_payload))
            logger.info(f"Recipient {recipient} notified for successfully starting onboarding process.")

    def _archive_current_organization(self, organization):
        if organization.get_status() == OrganizationStatus.PUBLISHED.value:
            org_repo.add_organization_archive(organization)

    def publish_org_to_ipfs(self):
        logger.info(f"publish organization to ipfs org_uuid: {self.org_uuid}")
        organization = org_repo.get_organization(org_uuid=self.org_uuid)
        organization.publish_to_ipfs()
        org_repo.store_ipfs_hash(organization, self.username)
        return organization.to_response()

    def save_transaction_hash_for_publish_org(self, payload):
        transaction_hash = payload.get("transaction_hash")
        if transaction_hash is None:
            raise BadRequestException()
        user_address = payload.get("wallet_address")
        nonce = payload.get("nonce")
        logger.info(f"save transaction hash for publish organization org_uuid: {self.org_uuid} "
                    f"transaction_hash: {transaction_hash} user_address: {user_address} nonce: {nonce}")
        org_repo.persist_publish_org_transaction_hash(self.org_uuid, transaction_hash, user_address, nonce,
                                                      self.username)
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
        org_repo.delete_members(org_member_list, member_status=[OrganizationMemberStatus.PENDING.value,
                                                                OrganizationMemberStatus.ACCEPTED.value])
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

        organization = org_repo.get_organization(org_uuid=self.org_uuid)
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
            mail_template = get_org_member_invite_mail(org_name, org_member.invite_code)
            send_notification_payload = {"body": json.dumps({
                "message": mail_template["body"],
                "subject": mail_template["subject"],
                "notification_type": "support",
                "recipient": recipient})}
            self.boto_utils.invoke_lambda(lambda_function_arn=registry.config.NOTIFICATION_ARN, invocation_type="RequestResponse",
                                          payload=json.dumps(send_notification_payload))
            logger.info(f"Org Membership Invite sent to {recipient}")

    def update_verification(self, verification_type, verification_details):
        if verification_type in ORG_TYPE_VERIFICATION_TYPE_MAPPING:
            if ORG_TYPE_VERIFICATION_TYPE_MAPPING[verification_type] == OrganizationType.INDIVIDUAL.value:
                owner_username = verification_details["username"]
                status = verification_details["status"]
                updated_by = verification_details["updated_by"]
                org_repo.update_all_individual_organization_for_user(owner_username, status, updated_by)

            elif ORG_TYPE_VERIFICATION_TYPE_MAPPING[verification_type] == OrganizationType.ORGANIZATION.value:
                status = verification_details["status"]
                org_uuid = verification_details["org_uuid"]
                updated_by = verification_details["updated_by"]
                comment = verification_details["comment"]
                if status in ORG_STATUS_LIST:
                    org_repo.update_organization_status(org_uuid, status, updated_by)
                    organization = org_repo.get_organization(org_uuid=org_uuid)
                    owner = org_repo.get_org_member(org_uuid=org_uuid, role=Role.OWNER.value)
                    owner_username = owner[0].username
                    self.send_mail_to_owner(owner_username, comment, organization.id, status)
                else:
                    logger.error(f"Invalid status {status}")
                    raise MethodNotImplemented()
            else:
                logger.error(f"Invalid organization type with verification type {verification_type}")
                raise MethodNotImplemented()
        else:
            logger.error(f"Invalid verification type {verification_type}")
            raise MethodNotImplemented()
        return {}

    def send_mail_to_owner(self, owner_email_address, comment, org_id, status):
        if status == OrganizationStatus.REJECTED.value:
            mail_template = get_owner_mail_for_org_rejected(org_id, comment)
        elif status == OrganizationStatus.CHANGE_REQUESTED.value:
            mail_template = get_owner_mail_for_org_changes_requested(org_id, comment)
        elif status == OrganizationStatus.APPROVED.value:
            mail_template = get_owner_mail_for_org_approved(org_id)
        else:
            logger.info(f"Organization status: {status}")
            raise InvalidOrganizationStateException()

        utils.send_email_notification([owner_email_address], mail_template["subject"],
                                      mail_template["body"], registry.config.NOTIFICATION_ARN, self.boto_utils)
