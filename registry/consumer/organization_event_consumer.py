import os
import traceback

from web3 import Web3

from common import blockchain_util
from common import ipfs_util
from common.logger import get_logger
from registry.config import NETWORK_ID, CONTRACT_BASE_PATH
from registry.constants import OrganizationMemberStatus, OrganizationStatus, Role, EnvironmentType
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.models.organization import Organization
from registry.domain.services.registry_blockchain_util import RegistryBlockChainUtil
from registry.exceptions import OrganizationNotFoundException

logger = get_logger(__name__)

BLOCKCHAIN_USER = "BLOCKCHAIN_EVENT"


class OrganizationEventConsumer(object):

    def __init__(self, ws_provider, ipfs_url, ipfs_port, organization_repository):
        self._ipfs_util = ipfs_util.IPFSUtil(ipfs_url, ipfs_port)
        self._blockchain_util = blockchain_util.BlockChainUtil("WS_PROVIDER", ws_provider)
        self._organization_repository = organization_repository

    def on_event(self, event):
        pass

    def _get_org_id_from_event(self, event):
        event_org_data = eval(event['data']['json_str'])
        org_id_bytes = event_org_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\x00")
        return org_id

    @staticmethod
    def _get_base_contract_path():
        return os.path.abspath(os.path.join(f"{CONTRACT_BASE_PATH}/node_modules/singularitynet-stake-contracts"))

    def _get_registry_contract(self):
        net_id = NETWORK_ID
        base_contract_path = self._get_base_contract_path()
        registry_contract = self._blockchain_util.get_contract_instance(base_contract_path, 'REGISTRY', net_id=net_id)

        return registry_contract

    def _get_tarnsaction_hash(self, event):
        return event['data']['transactionHash']

    def _get_org_details_from_blockchain(self, event):
        logger.info(f"processing org event {event}")

        registry_contract = self._get_registry_contract()
        org_id = self._get_org_id_from_event(event)
        transaction_hash = self._get_tarnsaction_hash(event)

        blockchain_org_data = registry_contract.functions.getOrganizationById(org_id.encode('utf-8')).call()
        org_metadata_uri = Web3.toText(blockchain_org_data[2]).rstrip("\x00").lstrip("ipfs://")
        ipfs_org_metadata = self._ipfs_util.read_file_from_ipfs(org_metadata_uri)
        owner = blockchain_org_data[3]
        members = blockchain_org_data[4]
        self._remove_owner_from_members(members, owner)
        return org_id, ipfs_org_metadata, org_metadata_uri, transaction_hash, owner, members

    def _remove_owner_from_members(self, members, owner):
        if owner in members:
            members.remove(owner)

    def _process_members(self, org_uuid, received_owner, existing_members, received_members):

        added_member = []
        removed_member = []
        updated_members = []
        recieved_members_map = {}
        existing_members_map = {}
        for recieved_member in received_members:
            recieved_member.set_status(OrganizationMemberStatus.PUBLISHED.value)
            recieved_members_map[recieved_member.address] = recieved_member

        existing_owner = None
        for existing_member in existing_members:
            existing_member.set_status(OrganizationMemberStatus.PUBLISHED.value)
            if existing_member.role == Role.OWNER.value:
                existing_owner = existing_member
                existing_members.remove(existing_member)
            else:
                existing_members_map[existing_member.address] = existing_member

        if not existing_owner or not existing_owner.address:
            self._organization_repository.add_member([received_owner])
        else:
            if existing_owner.address == received_owner.address:
                existing_owner.set_status(OrganizationMemberStatus.PUBLISHED.value)
                self._organization_repository.update_org_member_using_address(org_uuid, existing_owner,
                                                                              existing_owner.address)
            else:
                self._organization_repository.delete_published_members([existing_owner])
                self._organization_repository.add_member([received_owner])

        for recieved_member in received_members:
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
            self._organization_repository.delete_published_members(removed_member)
        if len(added_member) > 0:
            self._organization_repository.add_member(added_member)

        for member in updated_members:
            self._organization_repository.update_org_member_using_address(org_uuid, member, member.address)


class OrganizationCreatedAndModifiedEventConsumer(OrganizationEventConsumer):

    def on_event(self, event):
        org_id, ipfs_org_metadata, org_metadata_uri, transaction_hash, owner, recieved_members = self._get_org_details_from_blockchain(
            event)
        self._process_organization_create_event(org_id, ipfs_org_metadata, org_metadata_uri, transaction_hash, owner,
                                                recieved_members)

    def _get_existing_organization_records(self, org_id):
        try:
            existing_publish_in_progress_organization = self._organization_repository.get_organization(org_id=org_id)
        except OrganizationNotFoundException:
            return None
        except Exception as e:
            raise e

        return existing_publish_in_progress_organization

    def _mark_existing_publish_in_progress_as_published(self, existing_publish_in_progress_organization,
                                                        test_transaction_hash):
        self._organization_repository.update_organization(
            existing_publish_in_progress_organization, BLOCKCHAIN_USER, OrganizationStatus.PUBLISHED.value,
            test_transaction_hash=test_transaction_hash)

    def _create_event_outside_publisher_portal(self, received_organization_event, test_transaction_hash):
        self._organization_repository.store_organization(
            received_organization_event, BLOCKCHAIN_USER, OrganizationStatus.PUBLISHED_UNAPPROVED.value,
            test_transaction_hash=test_transaction_hash
        )

    def _process_organization_create_event(self, org_id, ipfs_org_metadata, org_metadata_uri, transaction_hash, owner,
                                           recieved_members_list):
        try:

            existing_publish_in_progress_organization = self._get_existing_organization_records(org_id)

            org_id = ipfs_org_metadata.get("org_id", None)
            org_name = ipfs_org_metadata.get("org_name", None)
            org_type = ipfs_org_metadata.get("org_type", None)
            description = ipfs_org_metadata.get("description", {})
            short_description = description.get("short_description", "")
            long_description = description.get("description", "")
            url = description.get("url", "")
            contacts = ipfs_org_metadata.get("contacts", None)
            raw_assets = ipfs_org_metadata.get("assets", {})
            assets = OrganizationFactory.parse_organization_metadata_assets(raw_assets, {})
            raw_groups = ipfs_org_metadata.get("groups", [])
            groups = OrganizationFactory.group_domain_entity_from_group_list_metadata(raw_groups)

            org_uuid = ""
            origin = ""
            duns_no = ""
            addresses = []
            members = []

            received_organization_event = Organization(org_uuid, org_id, org_name, org_type,
                                                       origin, long_description,
                                                       short_description, url, contacts, assets, org_metadata_uri,
                                                       duns_no, groups,
                                                       addresses,
                                                       OrganizationStatus.DRAFT.value,
                                                       members)

            if not existing_publish_in_progress_organization:
                existing_members = []

                received_organization_event.setup_id()
                org_uuid = received_organization_event.uuid
                self._create_event_outside_publisher_portal(received_organization_event, "")

            elif existing_publish_in_progress_organization.org_state.transaction_hash != transaction_hash \
                    and existing_publish_in_progress_organization.is_blockchain_major_change(received_organization_event)[0]:

                org_uuid = existing_publish_in_progress_organization.uuid
                logger.info(f"Detected Major change for {org_uuid}")
                existing_members = self._organization_repository.get_org_member(
                    org_uuid=existing_publish_in_progress_organization.uuid)
                self._organization_repository.store_organization(
                    existing_publish_in_progress_organization, BLOCKCHAIN_USER,
                    OrganizationStatus.APPROVAL_PENDING.value, test_transaction_hash="")
            else:
                org_uuid = existing_publish_in_progress_organization.uuid
                existing_members = self._organization_repository.get_org_member(
                    org_uuid=existing_publish_in_progress_organization.uuid)
                self._mark_existing_publish_in_progress_as_published(existing_publish_in_progress_organization, "")
            owner = OrganizationFactory.parser_org_owner_from_metadata(org_uuid, owner,
                                                                       OrganizationMemberStatus.PUBLISHED.value)
            recieved_members = OrganizationFactory.parser_org_members_from_metadata(org_uuid, recieved_members_list,
                                                                                    OrganizationMemberStatus.PUBLISHED.value)

            self._process_members(org_uuid, owner, existing_members, recieved_members)
        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise Exception(f"Error while processing org created event for org_id {org_id}")
