import os
from uuid import uuid4

from web3 import Web3

from common.blockchain_util import BlockChainUtil
from common.ipfs_util import IPFSUtil
from common.logger import get_logger
from registry.config import NETWORK_ID
from registry.constants import ServiceStatus
from registry.domain.factory.service_factory import ServiceFactory

logger = get_logger(__name__)


class ServiceEventConsumer(object):

    def __init__(self, ws_provider, ipfs_url, ipfs_port, service_repository, organiztion_repository):
        self._blockchain_util = BlockChainUtil("WS_PROVIDER", ws_provider)
        self._service_repository = service_repository
        self._organiztion_repository = organiztion_repository
        self._ipfs_util = IPFSUtil(ipfs_url, ipfs_port)

    def on_event(self, event):
        pass

    def _fetch_tags(self, registry_contract, org_id_hex, service_id_hex):
        tags_data = registry_contract.functions.getServiceRegistrationById(
            org_id_hex, service_id_hex).call()

        str_tag_data = []
        for tag in tags_data[3]:
            str_tag_data.append(tag.decode())
        return str_tag_data

    def _get_org_id_from_event(self, event):
        event_data = event['data']
        service_data = eval(event_data['json_str'])
        org_id_bytes = service_data['orgId']
        org_id = Web3.toText(org_id_bytes).rstrip("\x00")
        return org_id

    def _get_service_id_from_event(self, event):
        event_data = event['data']
        service_data = eval(event_data['json_str'])
        service_id_bytes = service_data['serviceId']
        service_id = Web3.toText(service_id_bytes).rstrip("\x00")
        return service_id

    def _get_metadata_uri_from_event(self, event):
        event_data = event['data']
        service_data = eval(event_data['json_str'])
        metadata_uri = Web3.toText(service_data['metadataURI'])[7:].rstrip("\u0000")
        return metadata_uri

    def _get_registry_contract(self):
        net_id = NETWORK_ID
        base_contract_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'node_modules', 'singularitynet-platform-contracts'))
        registry_contract = self._blockchain_util.get_contract_instance(base_contract_path, "REGISTRY", net_id)
        return registry_contract

    def _get_service_details_from_blockchain(self, event):
        logger.info(f"processing service event {event}")

        registry_contract = self._get_registry_contract()
        org_id = self._get_org_id_from_event(event)
        service_id = self._get_service_id_from_event(event)

        tags_data = self._fetch_tags(
            registry_contract=registry_contract, org_id_hex=org_id.encode("utf-8"),
            service_id_hex=service_id.encode("utf-8"))

        return org_id, service_id, tags_data


class ServiceCreatedEventConsumer(ServiceEventConsumer):

    def on_event(self, event):
        org_id, service_id, tags_data = self._get_service_details_from_blockchain(event)
        metadata_uri = self._get_metadata_uri_from_event(event)
        service_ipfs_data = self._ipfs_util.read_file_from_ipfs(metadata_uri)
        self._process_service_data(org_id=org_id, service_id=service_id,
                                   event_ipfs_data=service_ipfs_data, tags_data=tags_data)

    def _get_existing_service_details(self, org_id, service_id):
        org_uuid,existing_service = self._service_repository.get_service_for_given_service_id_and_org_id(org_id, service_id)

        return org_uuid,existing_service

    def _process_service_data(self, org_id, service_id, event_ipfs_data, tags_data):

        org_uuid, existing_service = self._get_existing_service_details(org_id, service_id)

        if existing_service:
            service_uuid = existing_service.uuid
        else:
            service_uuid = uuid4().hex

        recieved_service = ServiceFactory.create_service_from_service_metadata(org_uuid, service_uuid,
                                                                               event_ipfs_data, tags_data,
                                                                               ServiceStatus.DRAFT.value)
        if not existing_service:
            self._service_repository.add_service(recieved_service, "")

        elif existing_service.is_major_change(recieved_service):
            self._service_repository.save_service(recieved_service, ServiceStatus.DRAFT.value)
        else:
            self._service_repository.save_service("", recieved_service, ServiceStatus.PUBLISHED.value)
