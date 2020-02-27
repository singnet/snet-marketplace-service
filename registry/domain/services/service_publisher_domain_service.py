import web3
from registry.domain.factory.service_factory import ServiceFactory
from registry.constants import ServiceStatus, REG_CNTRCT_PATH, REG_ADDR_PATH
from registry.exceptions import ServiceProtoNotFoundException, OrganizationNotFoundException
from common.utils import publish_zip_file_in_ipfs, hash_to_bytesuri, json_to_file
from registry.config import ASSET_DIR, METADATA_FILE_PATH, ORG_ID_FOR_TESTING_AI_SERVICE, IPFS_URL, NETWORK_ID, \
    NETWORKS, EXECUTOR_KEY, EXECUTOR_ADDRESS
from common.ipfs_util import IPFSUtil
from common.blockchain_util import BlockChainUtil
from common.logger import get_logger
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

service_factory = ServiceFactory()
ipfs_client = IPFSUtil(IPFS_URL['url'], IPFS_URL['port'])
blockchain_util = BlockChainUtil(provider=NETWORKS[NETWORK_ID]["http_provider"], provider_type="HTTP_PROVIDER")
logger = get_logger(__name__)
METADATA_URI_PREFIX = "ipfs://"


class ServicePublisherDomainService:
    def __init__(self, username, org_uuid, service_uuid):
        self._username = username
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid

    @staticmethod
    def publish_service_proto_to_ipfs(service):
        proto_url = service.assets.get("proto_files", {}).get("url", None)
        if proto_url is None:
            raise ServiceProtoNotFoundException
        proto_ipfs_hash = publish_zip_file_in_ipfs(file_url=proto_url,
                                                   file_dir=f"{ASSET_DIR}/{service.org_uuid}/{service.uuid}",
                                                   ipfs_client=ipfs_client)
        service.proto = {
            "model_ipfs_hash": proto_ipfs_hash,
            "encoding": "proto",
            "service_type": "grpc"
        }
        service.assets["proto_files"]["ipfs_hash"] = proto_ipfs_hash
        return service

    @staticmethod
    def publish_service_metadata_to_ipfs(service):
        service_metadata = service.to_metadata()
        filename = f"{METADATA_FILE_PATH}/{service.uuid}_service_metadata.json"
        json_to_file(service_metadata, filename)
        metadata_ipfs_hash = ipfs_client.write_file_in_ipfs(filename, wrap_with_directory=False)
        service.metadata_uri = METADATA_URI_PREFIX + metadata_ipfs_hash
        return service

    @staticmethod
    def organization_exist_in_blockchain(org_id):
        # get list of organization from blockchain
        return True
        orgs = []
        if org_id in orgs:
            return True
        return False

    @staticmethod
    def service_exist_in_blockchain(org_id, service_id):
        # get list of services
        services = []
        if service_id in services:
            return True
        return False

    @staticmethod
    def update_service_in_blockchain(org_id, service_id, metadata_uri, tags):
        method_name = "updateServiceRegistration"
        positional_inputs = (org_id, service_id, metadata_uri, tags)
        transaction_object = blockchain_util.create_transaction_object(*positional_inputs, method_name=method_name,
                                                                       address=EXECUTOR_ADDRESS,
                                                                       contract_path=REG_CNTRCT_PATH,
                                                                       contract_address_path=REG_ADDR_PATH,
                                                                       net_id=NETWORK_ID)
        raw_transaction = blockchain_util.sign_transaction_with_private_key(transaction_object=transaction_object,
                                                                            private_key=EXECUTOR_KEY)
        transaction_hash = blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info(
            f"transaction hash {transaction_hash} generated while updating service {service_id} in test blockchain "
            f"environment.")
        return transaction_hash

    @staticmethod
    def register_service_in_blockchain(org_id, service_id, metadata_uri, tags):
        method_name = "createServiceRegistration"
        positional_inputs = (web3.Web3.toHex(text=ORG_ID_FOR_TESTING_AI_SERVICE),
                             web3.Web3.toHex(text=service_id),
                             metadata_uri, [web3.Web3.toHex(text=tag) for tag in tags])
        transaction_object = blockchain_util.create_transaction_object(*positional_inputs, method_name=method_name,
                                                                       address=EXECUTOR_ADDRESS,
                                                                       contract_path=REG_CNTRCT_PATH,
                                                                       contract_address_path=REG_ADDR_PATH,
                                                                       net_id=NETWORK_ID)
        raw_transaction = blockchain_util.sign_transaction_with_private_key(transaction_object=transaction_object,
                                                                            private_key=EXECUTOR_KEY)
        transaction_hash = blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info(
            f"transaction hash {transaction_hash} generated while registering service {service_id} in test blockchain "
            f"environment.")
        return transaction_hash

    @staticmethod
    def register_or_update_service_in_blockchain(org_id, service_id, metadata_uri, tags):
        if not ServicePublisherDomainService.organization_exist_in_blockchain(org_id=org_id):
            raise OrganizationNotFoundException()
        if ServicePublisherDomainService.service_exist_in_blockchain(org_id=org_id, service_id=service_id):
            # service exists in blockchain. update service in blockchain
            transaction_hash = ServicePublisherDomainService.update_service_in_blockchain(
                service_id=service_id, metadata_uri=metadata_uri, tags=tags)
        else:
            # service does not exists in blockchain. register service in blockchain
            transaction_hash = ServicePublisherDomainService.register_service_in_blockchain(
                org_id=org_id, service_id=service_id, metadata_uri=metadata_uri, tags=tags)
        return transaction_hash

    def validate_service_metadata(self):
        pass

    def submit_service_for_approval(self, payload):
        # service is submitted for approval. service state is APPROVAL PENDING.
        service = service_factory.create_service_entity_model(
            self._org_uuid, self._service_uuid, payload, ServiceStatus.APPROVAL_PENDING.value)

        # publish assets
        service = self.publish_service_proto_to_ipfs(service)
        service = self.publish_service_metadata_to_ipfs(service)
        service = ServicePublisherRepository().save_service(self._username, service, service.service_state.state)

        # deploy service on testing blockchain environment for verification
        transaction_hash = self.register_or_update_service_in_blockchain(
            org_id=ORG_ID_FOR_TESTING_AI_SERVICE, service_id=service.service_id,
            metadata_uri=hash_to_bytesuri(service.metadata_uri), tags=service.tags
        )
        return service.to_dict()
