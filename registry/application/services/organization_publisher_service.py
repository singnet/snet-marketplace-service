import json
from datetime import datetime, UTC
import tempfile
from typing import Union
from urllib.parse import urlparse

import requests
from web3 import Web3

from common import utils
from common.boto_utils import BotoUtils
from common.logger import get_logger
from registry.settings import settings
from registry.constants import (
    EnvironmentType,
    OrganizationActions,
    OrganizationIDAvailabilityStatus,
    OrganizationMemberStatus,
    OrganizationStatus,
    OrganizationType, 
    Role
)
from registry.infrastructure.storage_provider import (
    StorageProvider,
    StorageProviderType,
    FileUtils
)
from registry.application.schemas.organization import (
    GetGroupByOrganizationIdRequest,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    PublishOrganizationRequest,
    SaveTransactionHashForOrganizationRequest,
    GetAllMembersRequest,
    GetMemberRequest,
    InviteMembersRequest,
    VerifyCodeRequest,
    PublishMembersRequest,
    DeleteMembersRequest,
    RegisterMemberRequest,
    VerifyOrgRequest,
    VerifyOrgIdRequest
)
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.models.organization import Organization
from registry.domain.services.registry_blockchain_util import RegistryBlockChainUtil
from registry.exceptions import InvalidOrganizationStateException, BadRequestException, NewMemberAddressException
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository
from registry.mail_templates import (
    get_notification_mail_template_for_service_provider_when_org_is_submitted_for_onboarding,
    get_owner_mail_for_org_rejected,
    get_owner_mail_for_org_changes_requested,
    get_owner_mail_for_org_approved
)
from registry.mail_templates import get_org_member_invite_mail

org_repo = OrganizationPublisherRepository()

logger = get_logger(__name__)
ORG_APPROVE_SUBJECT = "Organization  {} Approved "
ORG_APPROVE_MESSAGE = "You organization  {} has been approved"


class OrganizationPublisherService:
    def __init__(self, lighthouse_token: Union[str, None] = None):
        self.boto_utils = BotoUtils(region_name=settings.aws.REGION_NAME)
        self.storage_provider = StorageProvider(lighthouse_token)

    def get_approval_pending_organizations(self, limit, type=None):
        status = OrganizationStatus.ONBOARDING.value
        organizations = org_repo.get_organizations(status, limit, type)
        return [org.to_response() for org in organizations]

    def get_all_org_for_user(self, username: str):
        logger.info(f"get organization for user: {username}")
        organizations = org_repo.get_all_orgs_for_user(username=username)
        return [org.to_response() for org in organizations]

    def get_all_org_id(self):
        organizations = org_repo.get_organizations()
        return [org.id for org in organizations]

    def get_org_id_availability_status(self, request: VerifyOrgIdRequest):
        org_id_list = self.get_all_org_id()

        if request.org_id in org_id_list:
            return OrganizationIDAvailabilityStatus.UNAVAILABLE.value
        if RegistryBlockChainUtil(EnvironmentType.MAIN.value).is_org_published(request.org_id):
            return OrganizationIDAvailabilityStatus.UNAVAILABLE.value
        return OrganizationIDAvailabilityStatus.AVAILABLE.value

    def get_groups_for_org(self, request: GetGroupByOrganizationIdRequest):
        groups = org_repo.get_groups_for_org(request.org_uuid)
        return {
            "org_uuid": request.org_uuid,
            "groups": [group.to_response() for group in groups]
        }

    def create_organization(self, username: str, request: CreateOrganizationRequest):
        organization = OrganizationFactory.create_organization_entity_from_request(request)
        organization.setup_id()
        logger.info(f"assigned org_uuid : {organization.uuid}")

        org_ids = self.get_all_org_id()
        if organization.id in org_ids:
            raise Exception("Org_id already exists")

        updated_state = Organization.next_state(None, None, OrganizationActions.CREATE.value)
        organization = org_repo.add_organization(organization, username, updated_state)

        return organization.to_response()

    #TODO: Review this method with frontend calls
    def update_organization(self, username: str, request: UpdateOrganizationRequest):
        updated_organization = OrganizationFactory.create_organization_entity_from_request(request)
        
        current_organization = org_repo.get_organization(org_uuid=request.uuid)
        self._archive_current_organization(current_organization)
        
        updated_state = Organization.next_state(current_organization, updated_organization, request.action)
        org_repo.update_organization(updated_organization, username, updated_state)
        
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
            self.boto_utils.invoke_lambda(
                lambda_function_arn=settings.lambda_arn.NOTIFICATION_ARN,
                invocation_type="RequestResponse",
                payload=json.dumps(send_notification_payload)
            )
            logger.info(f"Recipient {recipient} notified for successfully starting onboarding process.")

    def _archive_current_organization(self, organization):
        if organization.get_status() == OrganizationStatus.PUBLISHED.value:
            org_repo.add_organization_archive(organization)

    def publish_assets_to_storage_provider(self, organization: Organization, provider_type: StorageProviderType):
        for asset_type in organization.assets:
            if "url" in organization.assets[asset_type]:
                url = organization.assets[asset_type]["url"]
                filename = urlparse(url).path.split("/")[-1]

                response = requests.get(url)
                response.raise_for_status()

                with tempfile.NamedTemporaryFile(mode='wb', suffix=f"_{filename}", delete=True) as temp_asset_file:
                    temp_asset_file.write(response.content)
                    temp_asset_file.flush()

                    asset_hash = self.storage_provider.publish(temp_asset_file.name, provider_type)

                    organization.assets[asset_type]["hash"] = asset_hash

    def publish_metadata_to_storage_provider(self, organization: Organization, storage_type: StorageProviderType) -> str:
        self.publish_assets_to_storage_provider(organization, storage_type)
        filepath = FileUtils.create_temp_json_file(organization.to_metadata())
        return self.storage_provider.publish(filepath, storage_type)

    def publish_organization(self, username: str, request: PublishOrganizationRequest) -> dict:
        logger.debug(f"Publish organization {request.org_uuid} to {request.storage_provider}")

        organization = org_repo.get_organization(org_uuid=request.org_uuid)
        if organization is None:
            raise Exception("Get organization is None") #TODO: add exception

        organization.metadata_uri = self.publish_metadata_to_storage_provider(organization, request.storage_provider)
        org_repo.store_metadata_uri(organization, username)

        return organization.to_response()

    def save_transaction_hash_for_publish_org(self, username: str, request: SaveTransactionHashForOrganizationRequest):
        logger.info(f"save transaction hash for publish organization org_uuid: {request.org_uuid} "
                    f"transaction_hash: {request.transaction_hash} user_address: {request.wallet_address} nonce: {request.nonce}")
        org_repo.persist_publish_org_transaction_hash(
            org_uuid=request.org_uuid,
            transaction_hash=request.transaction_hash,
            wallet_address=request.wallet_address,
            nonce=request.nonce,
            username=username
        )

        return "OK"

    # TODO: Review rework this query and pagination
    def get_all_member(self, request: GetAllMembersRequest):
        # offset = pagination_details.get("offset", None)
        # limit = pagination_details.get("limit", None)
        # sort = pagination_details.get("sort", None)
        org_members_list = org_repo.get_org_member(
            org_uuid=request.org_uuid, status=request.status, role=request.role
        )
        return [member.to_response() for member in org_members_list]

    def get_member(self, username: str, request: GetMemberRequest):
        members = org_repo.get_org_member(username=request.member_username, org_uuid=request.org_uuid)
        if len(members) == 0:
            logger.info(f"No member {request.member_username} for the organization {request.org_uuid}")
            return []
        return [member.to_response() for member in members]

    def verify_invite(self, username: str, request: VerifyCodeRequest):
        logger.info(f"verify member invite_code: {request.invite_code} username: {username}")
        if org_repo.org_member_verify(username, request.invite_code):
            return "OK"
        return "NOT_FOUND"

    def delete_members(self, username: str, request: DeleteMembersRequest):
        logger.info(f"user: {username} requested to delete members: {request.members} of org_uuid: {request.org_uuid}")
        org_member_list = OrganizationFactory.org_member_domain_entity_from_payload_list(
            request.members, request.org_uuid
        )
        org_repo.delete_members(
            org_member_list,
            member_status=[
                OrganizationMemberStatus.PENDING.value,
                OrganizationMemberStatus.ACCEPTED.value
            ]
        )
        return "OK"

    def publish_members(self, username: str, request: PublishMembersRequest):
        logger.info(f"user: {username} published members: {request.members} with transaction_hash: {request.transaction_hash}")
        org_member = OrganizationFactory.org_member_domain_entity_from_payload_list(request.members, request.org_uuid)
        org_repo.persist_publish_org_member_transaction_hash(org_member, request.transaction_hash, request.org_uuid)
        return "OK"

    def register_member(self, username: str, request: RegisterMemberRequest):
        logger.info(f"register user: {username} with invite_code: {request.invite_code}")
        if Web3.is_address(request.wallet_address):
            org_uuid = org_repo.get_org_member(username = username, invite_code = request.invite_code)[0].org_uuid
            org_owner = org_repo.get_org_member(org_uuid = org_uuid, role = Role.OWNER.value)[0]
            if org_owner.address == request.wallet_address:
                raise NewMemberAddressException()
            org_repo.update_org_member(
                username, request.wallet_address, request.invite_code
            )
        else:
            raise Exception("Invalid wallet address")
        return "OK"

    def invite_members(self, request: InviteMembersRequest):
        current_time = datetime.now(UTC)
        requested_invite_member_list = OrganizationFactory.org_member_domain_entity_from_payload_list(
            request.members,
            request.org_uuid
        )
        current_org_member = org_repo.get_org_member(org_uuid=request.org_uuid)
        current_org_member_username_list = [member.username for member in current_org_member]
        eligible_invite_member_list = [member for member in requested_invite_member_list
                                       if member.username not in current_org_member_username_list]
        for org_member in eligible_invite_member_list:
            org_member.generate_invite_code()
            org_member.set_status(OrganizationMemberStatus.PENDING.value)
            org_member.set_role(Role.MEMBER.value)
            org_member.set_invited_on(current_time)
            org_member.set_updated_on(current_time)

        organization = org_repo.get_organization(org_uuid=request.org_uuid)
        
        if organization is None:
            raise Exception("Organization doesnt exist")
        
        self._send_email_notification_for_inviting_organization_member(
            eligible_invite_member_list, organization.name
        )
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
            self.boto_utils.invoke_lambda(
                lambda_function_arn=settings.lambda_arn.NOTIFICATION_ARN,
                invocation_type="RequestResponse",
                payload=json.dumps(send_notification_payload)
            )
            logger.info(f"Org Membership Invite sent to {recipient}")

    def update_verification(self, request: VerifyOrgRequest):       
        if request.org_type == OrganizationType.INDIVIDUAL.value:
            org_repo.update_all_individual_organization_for_user(
                request.username, request.status, request.updated_by
            )

        elif request.org_type == OrganizationType.ORGANIZATION.value:
            org_repo.update_organization_status(
                request.org_uuid, request.status, request.updated_by
            )
            organization = org_repo.get_organization(org_uuid=request.org_uuid)
            if organization is None:
                raise BadRequestException()

            owner = org_repo.get_org_member(
                org_uuid=request.org_uuid,
                role=Role.OWNER.value
            )
            owner_username = owner[0].username
            self.send_mail_to_owner(owner_username, request.comment, organization.id, request.status)

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

        utils.send_email_notification(
            [owner_email_address],
            mail_template["subject"],
            mail_template["body"],
            settings.lambda_arn.NOTIFICATION_ARN,
            self.boto_utils
        )
