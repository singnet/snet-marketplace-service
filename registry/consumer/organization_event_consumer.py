import os
import traceback

from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from registry.config import NETWORK_ID
from registry.constants import OrganizationStatus
from registry.consumer.event_consumer import EventConsumer
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.infrastructure.repositories.organization_repository import OrganizationRepository

logger = get_logger(__name__)

BLOCKCHAIN_USER = "BLOCKCHAIN_EVENT"


class OrganizationEventConsumer(EventConsumer):
    _organization_repository = OrganizationRepository()

    def __init__(self, ws_provider, ipfs_url, ipfs_port):
        self._ipfs_util = IPFSUtil(ipfs_url, ipfs_port)
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)

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

        return org_id, ipfs_org_metadata


class OrganizationCreatedEventConsumer(OrganizationEventConsumer):

    def on_event(self, event):
        org_id, ipfs_org_metadata = self._get_org_details_from_blockchain(event)
        self._process_organization_create_event(org_id, ipfs_org_metadata)

    def _get_existing_organization_records(self, org_id):
        existing_publish_in_progress_organization = self._organization_repository.get_org_with_status_using_org_id(
            org_id, OrganizationStatus.PUBLISH_IN_PROGRESS.value)
        return existing_publish_in_progress_organization

    def _mark_existing_publish_in_progress_as_published(self, existing_publish_in_progress_organization):
        self._organization_repository.change_org_status(existing_publish_in_progress_organization.org_uuid,
                                                        OrganizationStatus.PUBLISH_IN_PROGRESS.value,
                                                        OrganizationStatus.PUBLISHED.value, BLOCKCHAIN_USER
                                                        )

    def _create_event_outside_publisher_portal(self, received_organization_event):
        self._organization_repository.add_org_with_status(received_organization_event,
                                                          OrganizationStatus.APPROVAL_PENDING, BLOCKCHAIN_USER)

    def _process_organization_create_event(self, org_id, ipfs_org_metadata):
        try:

            existing_publish_in_progress_organization = self._get_existing_organization_records(org_id)

            received_organization_event = OrganizationFactory.parse_organization_metadata(ipfs_org_metadata)

            if len(existing_publish_in_progress_organization) == 0:
                self._create_event_outside_publisher_portal(received_organization_event)



            elif existing_publish_in_progress_organization[0].is_major_change(received_organization_event):
                self._organization_repository.add_org_with_status(received_organization_event,
                                                                  OrganizationStatus.APPROVAL_PENDING, BLOCKCHAIN_USER)
            else:
                self._mark_existing_publish_in_progress_as_published(existing_publish_in_progress_organization[0])

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise Exception(f"Error while processing org created event for org_id {org_id}")


class OrganizationModifiedEventConsumer(OrganizationEventConsumer):
    def on_event(self, event):
        org_id, ipfs_org_metadata = self._get_org_details_from_blockchain(event)
        self._process_organization_update_event(org_id, ipfs_org_metadata)

    def _get_organization_with_status(self, org_id, status):
        existing_organizations = self._organization_repository.get_org_with_status_using_org_id(
            org_id, status)
        return existing_organizations

    def _get_existing_organization_records(self, org_id):

        existing_publish_in_progress_organization = self._get_organization_with_status(org_id,
                                                                                       OrganizationStatus.PUBLISH_IN_PROGRESS.value)

        existing_published_organization = self._get_organization_with_status(org_id, OrganizationStatus.PUBLISHED.value)

        existing_draft_organization = self._get_organization_with_status(org_id, OrganizationStatus.DRAFT.value)

        return existing_publish_in_progress_organization, existing_published_organization, existing_draft_organization

    def _move_exsiting_published_record_to_histroy(self, existing_published_organization):
        # Move current published org record to  archive table marks this record as published
        self._organization_repository.move_org_to_history_with_status(existing_published_organization.org_uuid,
                                                                      OrganizationStatus.PUBLISHED.value)

    def _mark_existing_publish_in_progress_as_published(self, existing_publish_in_progress_organization):
        self._organization_repository.change_org_status(existing_publish_in_progress_organization.org_uuid,
                                                        OrganizationStatus.PUBLISH_IN_PROGRESS.value,
                                                        OrganizationStatus.PUBLISHED.value, BLOCKCHAIN_USER
                                                        )

    def _publish_and_update_existing_org_records(self, existing_publish_in_progress_organization,
                                                 existing_published_organization):
        self._move_exsiting_published_record_to_histroy(existing_published_organization)
        self._mark_existing_publish_in_progress_as_published(existing_publish_in_progress_organization)

    def _publish_in_progress_and_published_record_recieve_update_event(self, existing_publish_in_progress_organization,
                                                                       existing_published_organization,
                                                                       received_organization_event):

        if not existing_publish_in_progress_organization.is_major_change(received_organization_event):
            self._publish_and_update_existing_org_records(existing_publish_in_progress_organization,
                                                          existing_published_organization)
        else:
            self._organization_repository.add_org_with_status(existing_publish_in_progress_organization,
                                                              OrganizationStatus.APPROVAL_PENDING, BLOCKCHAIN_USER)

    def _update_event_outside_publisher_portal(self, received_organization_event):
        self._organization_repository.add_org_with_status(received_organization_event,
                                                          OrganizationStatus.APPROVAL_PENDING, BLOCKCHAIN_USER)

    def _draft_and_published_record_recieve_update_event(self, existing_draft_organization,
                                                         existing_published_organization, received_organization_event):
        if not existing_draft_organization.is_major_change(received_organization_event):
            self._publish_and_update_existing_org_records(existing_draft_organization,
                                                          existing_published_organization)
        else:
            self._organization_repository.add_org_with_status(existing_draft_organization,
                                                              OrganizationStatus.APPROVAL_PENDING, BLOCKCHAIN_USER)

    def _process_organization_update_event(self, org_id, ipfs_org_metadata):
        # In case of update one orgnaization record will be in published state
        # and one org record(latest changes) will be in publish in progress

        existing_publish_in_progress_organization, existing_published_organization, existing_draft_organization = self._get_existing_organization_records(
            org_id)
        received_organization_event = OrganizationFactory.parse_organization_metadata(ipfs_org_metadata)

        if len(existing_publish_in_progress_organization) > 0 and len(existing_published_organization) > 0:
            self._publish_in_progress_and_published_record_recieve_update_event(
                existing_publish_in_progress_organization[0],
                existing_published_organization[0],
                received_organization_event)


        elif len(existing_draft_organization) > 0 and len(existing_published_organization) > 0:
            self._draft_and_published_record_recieve_update_event(existing_draft_organization[0],
                                                                  existing_published_organization[0],
                                                                  received_organization_event)


        elif len(existing_published_organization) == 0:
            self._update_event_outside_publisher_portal(received_organization_event)

        else:
            raise Exception(f"Unknown scneario for organization {org_id} ")
