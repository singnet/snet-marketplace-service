import os
import traceback

from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from registry.config import NETWORK_ID
from registry.constants import OrganizationMemberStatus, OrganizationStatus, Role
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.exceptions import OrganizationNotFoundException

logger = get_logger(__name__)

BLOCKCHAIN_USER = "BLOCKCHAIN_EVENT"


class OrganizationEventConsumer(object):

    def __init__(self, ws_provider, ipfs_url, ipfs_port, organization_repository):
        self._ipfs_util = IPFSUtil(ipfs_url, ipfs_port)
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self._organization_repository = organization_repository

    def on_event(self, event):
        pass

    def _get_org_id_from_event(self, event):
        event_org_data = eval(event['data']['json_str'])
        org_id_bytes = event_org_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\x00")
        return org_id

    def _get_registry_contract(self):
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'node_modules', 'singularitynet-platform-contracts'))
        registry_contract = self._blockchain_util.get_contract_instance(base_contract_path, "REGISTRY", net_id)

        return registry_contract

    def _get_org_details_from_blockchain(self, event):
        logger.info(f"processing org event {event}")

        registry_contract = self._get_registry_contract()
        org_id = self._get_org_id_from_event(event)

        blockchain_org_data = registry_contract.functions.getOrganizationById(org_id.encode('utf-8')).call()
        org_metadata_uri = Web3.toText(blockchain_org_data[2]).rstrip("\x00").lstrip("ipfs://")
        ipfs_org_metadata = self._ipfs_util.read_file_from_ipfs(org_metadata_uri)
        members = blockchain_org_data[4]
        return org_id, ipfs_org_metadata, members

    def _process_members(self, org_uuid, existing_members, recieved_members):

        added_member = []
        removed_member = []
        updated_members = []
        recieved_members_map = {}
        existing_members_map = {}
        for recieved_member in recieved_members:
            recieved_member.set_status (OrganizationMemberStatus.PUBLISHED.value)
            recieved_members_map[recieved_member.address] = recieved_member

        for existing_member in existing_members:
            existing_member.set_status(OrganizationMemberStatus.PUBLISHED.value)
            if existing_member.role == Role.OWNER.value:
                self._organization_repository.update_org_member_using_address(org_uuid, existing_member, existing_member.address)
            else:
                existing_members_map[existing_member.address] = existing_member

        for recieved_member in recieved_members:
            if recieved_member.address in existing_members_map:
                updated_members.append(existing_members_map[recieved_member.address])
            else:
                added_member.append(recieved_member)

        for existing_member in existing_members:

            if existing_member.address in recieved_members_map:
                # already existing
                pass
            else:
                removed_member.append(existing_member)
        if len(removed_member) > 0:
            self._organization_repository.delete_members(removed_member)
        if len(added_member) > 0:
            self._organization_repository.add_member(added_member)

        for member in updated_members:
            self._organization_repository.update_org_member_using_address(org_uuid, member, member.address)


class OrganizationCreatedAndModifiedEventConsumer(OrganizationEventConsumer):

    def on_event(self, event):
        org_id, ipfs_org_metadata, recieved_members = self._get_org_details_from_blockchain(event)
        self._process_organization_create_event(org_id, ipfs_org_metadata, recieved_members)

    def _get_existing_organization_records(self, org_id):
        try:
            existing_publish_in_progress_organization = self._organization_repository.get_org_for_org_id(
                org_id)
        except OrganizationNotFoundException:
            return None
        except Exception as e:
            raise e

        return existing_publish_in_progress_organization

    def _mark_existing_publish_in_progress_as_published(self, existing_publish_in_progress_organization):
        self._organization_repository.update_organization(existing_publish_in_progress_organization,
                                                          BLOCKCHAIN_USER,
                                                          OrganizationStatus.PUBLISHED.value)

    def _create_event_outside_publisher_portal(self, received_organization_event):
        self._organization_repository.store_organization(received_organization_event, BLOCKCHAIN_USER,
                                                         OrganizationStatus.PUBLISHED_UNAPPROVED.value
                                                         )

    def _process_organization_create_event(self, org_id, ipfs_org_metadata, recieved_members_list):
        try:

            existing_publish_in_progress_organization = self._get_existing_organization_records(org_id)
            if existing_publish_in_progress_organization:
                org_uuid = existing_publish_in_progress_organization.uuid
            else:
                org_uuid = ""

            received_organization_event = OrganizationFactory.parse_organization_metadata(org_uuid, ipfs_org_metadata)

            if not existing_publish_in_progress_organization:
                existing_members = []
                received_organization_event.setup_id()
                self._create_event_outside_publisher_portal(received_organization_event)

            elif existing_publish_in_progress_organization.is_major_change(received_organization_event):
                org_uuid = existing_publish_in_progress_organization.uuid
                existing_members = self._organization_repository.get_org_member(org_uuid=
                                                                                existing_publish_in_progress_organization.uuid)
                self._organization_repository.store_organization(received_organization_event, BLOCKCHAIN_USER,
                                                                 OrganizationStatus.APPROVAL_PENDING)
            else:
                org_uuid = existing_publish_in_progress_organization.uuid
                existing_members = self._organization_repository.get_org_member(
                    org_uuid=existing_publish_in_progress_organization.uuid)
                self._mark_existing_publish_in_progress_as_published(received_organization_event)

            recieved_members = OrganizationFactory.parser_org_members_from_metadata(org_uuid, recieved_members_list,
                                                                                    OrganizationMemberStatus.PUBLISHED.value)

            self._process_members(org_uuid, existing_members, recieved_members)
        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise Exception(f"Error while processing org created event for org_id {org_id}")

