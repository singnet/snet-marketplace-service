import ast
import os
import traceback
from typing import List, Dict

from web3 import Web3

from common import blockchain_util
from common.logger import get_logger
from registry.domain.models.organization_member import OrganizationMember
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

from registry.settings import settings
from registry.constants import (
    OrganizationMemberStatus,
    OrganizationStatus,
    Role,
    SmartContracts,
)

from registry.domain.factory.organization_factory import OrganizationFactory
from registry.domain.models.organization import Organization
from registry.exceptions import OrganizationNotFoundException
from registry.infrastructure.storage_provider import StorageProvider


logger = get_logger(__name__)
BLOCKCHAIN_USER = "BLOCKCHAIN_EVENT"
NETWORK_ID = settings.network.id
CONTRACT_BASE_PATH = settings.network.networks[NETWORK_ID].contract_base_path


class OrganizationEventConsumer:
    def __init__(self, ws_provider, organization_repository):
        self.__storage_provider = StorageProvider()
        self._blockchain_util = blockchain_util.BlockChainUtil(
            "WS_PROVIDER", ws_provider
        )
        self._organization_repository: OrganizationPublisherRepository = organization_repository

    def on_event(self, event):
        pass

    def _get_org_id_from_event(self, event):
        event_org_data = ast.literal_eval(event["data"]["json_str"])
        org_id_bytes = event_org_data["orgId"]
        org_id = Web3.to_text(org_id_bytes).rstrip("\x00")
        return org_id

    @staticmethod
    def _get_base_contract_path():
        return os.path.abspath(
            os.path.join(
                f"{CONTRACT_BASE_PATH}/node_modules/singularitynet-platform-contracts"
            )
        )

    def _get_registry_contract(self):
        base_contract_path = self._get_base_contract_path()
        registry_contract = self._blockchain_util.get_contract_instance(
            base_contract_path,
            SmartContracts.REGISTRY.value,
            NETWORK_ID,
            settings.token_name,
            settings.stage,
        )

        return registry_contract

    def _get_transaction_hash(self, event):
        return event["data"]["transaction_hash"]

    def _get_org_details_from_blockchain(self, event):
        logger.info(f"processing org event {event}")

        registry_contract = self._get_registry_contract()
        org_id = self._get_org_id_from_event(event)
        transaction_hash = self._get_transaction_hash(event)

        encoded_org_id = Web3.to_bytes(text = org_id).ljust(32, b'\0')[:32]
        blockchain_org_data = registry_contract.functions.getOrganizationById(
            encoded_org_id
        ).call()
        logger.info(f"blockchain org data {blockchain_org_data}")

        org_metadata_uri = Web3.to_text(blockchain_org_data[2]).rstrip("\x00")
        logger.info(f"org metadata uri {org_metadata_uri}")

        org_metadata = self.__storage_provider.get(org_metadata_uri)
        owner = blockchain_org_data[3]
        members = blockchain_org_data[4]
        self._remove_owner_from_members(members, owner)

        return org_id, org_metadata, org_metadata_uri, transaction_hash, owner, members

    def _remove_owner_from_members(self, members, owner):
        if owner in members:
            members.remove(owner)

    def _process_owner(self, org_uuid: str, owner_address: str, current_members_map: Dict[str, OrganizationMember]):
        owner = current_members_map.get(owner_address, None)
        if owner is None:
            owner = OrganizationMember(
                org_uuid=org_uuid,
                role=Role.OWNER.value,
                status=OrganizationMemberStatus.PUBLISHED.value,
                address=owner_address,
                username="",
            )
        else:
            owner.set_status(OrganizationMemberStatus.PUBLISHED.value)
            owner.set_role(Role.OWNER.value)

        self._organization_repository.upsert_org_member(owner)

        # delete other owners
        current_members_map[owner_address] = owner
        for address, member in current_members_map.items():
            if member.role != Role.OWNER.value:
                continue
            if address != owner_address or member.status != OrganizationMemberStatus.PUBLISHED.value or member.username != owner.username:
                self._organization_repository.delete_org_member(member)

    def _process_members(self, org_uuid: str, member_addresses: List[str], current_members_map: Dict[str, OrganizationMember]):
        for member_address in member_addresses:
            member = current_members_map.get(member_address, None)
            if member_address not in current_members_map:
                member = OrganizationMember(
                    org_uuid=org_uuid,
                    role=Role.MEMBER.value,
                    status=OrganizationMemberStatus.PUBLISHED.value,
                    address=member_address,
                    username="",
                )
            else:
                member.set_status(OrganizationMemberStatus.PUBLISHED.value)
                member.set_role(Role.MEMBER.value)
            self._organization_repository.upsert_org_member(member)

    def _update_org_members(self, org_uuid: str, owner_address: str, member_addresses: List[str]):
        current_members = self._organization_repository.get_org_member(org_uuid=org_uuid)
        current_members_map = {member.address: member for member in current_members if member.address is not None}
        logger.info(f"Current members: {current_members_map}")
        logger.info(f"Owner address: {owner_address}")
        logger.info(f"Member addresses: {member_addresses}")

        self._process_owner(org_uuid, owner_address, current_members_map)
        self._process_members(org_uuid, member_addresses, current_members_map)


class OrganizationCreatedAndModifiedEventConsumer(OrganizationEventConsumer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_event(self, event):
        (
            org_id,
            org_metadata,
            org_metadata_uri,
            transaction_hash,
            owner,
            recieved_members,
        ) = self._get_org_details_from_blockchain(event)
        self._process_organization_create_event(
            org_id,
            org_metadata,
            org_metadata_uri,
            transaction_hash,
            owner,
            recieved_members,
        )

    def _get_existing_organization_records(self, org_id):
        try:
            existing_publish_in_progress_organization = (
                self._organization_repository.get_organization(org_id=org_id)
            )
        except OrganizationNotFoundException:
            return None
        except Exception as e:
            raise e

        return existing_publish_in_progress_organization

    def _mark_existing_publish_in_progress_as_published(
        self, existing_publish_in_progress_organization, test_transaction_hash
    ):
        self._organization_repository.update_organization(
            existing_publish_in_progress_organization,
            BLOCKCHAIN_USER,
            OrganizationStatus.PUBLISHED.value,
            test_transaction_hash=test_transaction_hash,
        )

    def _create_event_outside_publisher_portal(
        self, received_organization_event, test_transaction_hash
    ):
        self._organization_repository.store_organization(
            received_organization_event,
            BLOCKCHAIN_USER,
            OrganizationStatus.PUBLISHED_UNAPPROVED.value,
            test_transaction_hash=test_transaction_hash,
        )

    def _process_organization_create_event(
        self,
        org_id,
        org_metadata,
        org_metadata_uri,
        transaction_hash,
        owner,
        received_members_list,
    ):
        try:
            existing_publish_in_progress_organization = (
                self._get_existing_organization_records(org_id)
            )

            org_id = org_metadata.get("org_id", None)
            org_name = org_metadata.get("org_name", None)
            org_type = org_metadata.get("org_type", None)
            description = org_metadata.get("description", {})
            short_description = description.get("short_description", "")
            long_description = description.get("description", "")
            url = description.get("url", "")
            contacts = org_metadata.get("contacts", None)
            raw_assets = org_metadata.get("assets", {})
            assets = OrganizationFactory.parse_organization_metadata_assets(
                raw_assets, {}
            )
            raw_groups = org_metadata.get("groups", [])
            groups = OrganizationFactory.group_domain_entity_from_group_list_metadata(
                raw_groups
            )

            org_uuid = ""
            origin = ""
            duns_no = ""
            addresses = []
            members = []

            received_organization_event = Organization(
                org_uuid,
                org_id,
                org_name,
                org_type,
                origin,
                long_description,
                short_description,
                url,
                contacts,
                assets,
                org_metadata_uri,
                duns_no,
                groups,
                addresses,
                OrganizationStatus.DRAFT.value,
                members,
            )

            if not existing_publish_in_progress_organization:
                logger.info(f"The first path has chosen")

                received_organization_event.setup_id()
                org_uuid = received_organization_event.uuid
                self._create_event_outside_publisher_portal(
                    received_organization_event, ""
                )

            elif (
                existing_publish_in_progress_organization.org_state.transaction_hash
                != transaction_hash
                and existing_publish_in_progress_organization.is_blockchain_major_change(
                    received_organization_event
                )[0]
            ):
                logger.info(f"The second path has chosen")

                org_uuid = existing_publish_in_progress_organization.uuid
                logger.info(f"Detected Major change for {org_uuid}")
                self._organization_repository.store_organization(
                    existing_publish_in_progress_organization,
                    BLOCKCHAIN_USER,
                    OrganizationStatus.APPROVAL_PENDING.value,
                    test_transaction_hash="",
                )

            else:
                logger.info(f"The third path has chosen")

                org_uuid = existing_publish_in_progress_organization.uuid
                self._mark_existing_publish_in_progress_as_published(
                    existing_publish_in_progress_organization, ""
                )

            self._update_org_members(org_uuid, owner, received_members_list)

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise Exception(
                f"Error while processing org created event for org_id {org_id}"
            )
