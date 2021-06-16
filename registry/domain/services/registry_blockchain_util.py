import web3

from common.blockchain_util import BlockChainUtil
from common.boto_utils import BotoUtils
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from common.utils import ipfsuri_to_bytesuri, hash_to_bytesuri
from registry.config import NETWORK_ID, NETWORKS, BLOCKCHAIN_TEST_ENV, REGION_NAME
from registry.constants import EnvironmentType, REG_CNTRCT_PATH, REG_ADDR_PATH, TEST_REG_CNTRCT_PATH, TEST_REG_ADDR_PATH
from registry.exceptions import OrganizationNotFoundException, EnvironmentNotFoundException

logger = get_logger(__name__)


class RegistryBlockChainUtil:
    def __init__(self, env_type):
        self.__env_type = env_type
        if env_type == EnvironmentType.MAIN.value:
            self.__network_id = NETWORK_ID
            self.__contract_path = REG_CNTRCT_PATH
            self.__executor_address = ""
            self.__contract_address_path = REG_ADDR_PATH
            self.__blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
                                                    provider=NETWORKS[self.__network_id]['http_provider'])

        # elif env_type == EnvironmentType.TEST.value:
        #     self.__contract_path = TEST_REG_CNTRCT_PATH
        #     self.__contract_address_path = TEST_REG_ADDR_PATH
        #     self.__executor_address = BLOCKCHAIN_TEST_ENV["publisher_address"]
        #     self.__network_id = BLOCKCHAIN_TEST_ENV["network_id"]
        #     self.__blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
        #                                             provider=BLOCKCHAIN_TEST_ENV['http_provider'])
        else:
            raise MethodNotImplemented()

    def is_org_published(self, org_id):
        contract = self.__blockchain_util.load_contract(path=self.__contract_path)
        contract_address = self.__blockchain_util.read_contract_address(
            net_id=self.__network_id, path=self.__contract_address_path, key='address')
        return self.__organization_exist_in_blockchain(org_id, contract, contract_address)

    def __organization_exist_in_blockchain(self, org_id, contract, contract_address):
        method_name = "getOrganizationById"
        positional_inputs = (web3.Web3.toHex(text=org_id),)
        contract = self.__blockchain_util.contract_instance(contract_abi=contract, address=contract_address)

        org_data = self.__blockchain_util.call_contract_function(
            contract=contract, contract_function=method_name, positional_inputs=positional_inputs)

        logger.info(f"Org data :: {org_data}")
        org_found = org_data[0]
        return org_found

    # def __generate_blockchain_transaction_for_test_environment(self, *positional_inputs, method_name):
    #     transaction_object = self.__blockchain_util.create_transaction_object(
    #         *positional_inputs, method_name=method_name, address=self.__executor_address,
    #         contract_path=self.__contract_path, contract_address_path=self.__contract_address_path,
    #         net_id=self.__network_id)
    #     return transaction_object

    # def __make_trasaction(self, *positional_inputs, method_name):
    #     if self.__env_type == EnvironmentType.TEST.value:
    #         executor_key = BotoUtils(REGION_NAME).get_ssm_parameter(BLOCKCHAIN_TEST_ENV["publisher_private_key"])
    #         transaction_object = self.__generate_blockchain_transaction_for_test_environment(
    #             *positional_inputs, method_name=method_name)
    #     else:
    #         raise EnvironmentNotFoundException()
    #     raw_transaction = self.__blockchain_util.sign_transaction_with_private_key(
    #         transaction_object=transaction_object,
    #         private_key=executor_key)
    #     transaction_hash = self.__blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
    #     return transaction_hash

    # def __update_organization_in_blockchain(self, org_id, metadata_uri):
    #     method_name = "changeOrganizationMetadataURI"
    #     positional_inputs = (web3.Web3.toHex(text=org_id), hash_to_bytesuri(metadata_uri))
    #     transaction_hash = self.__make_trasaction(*positional_inputs, method_name=method_name)
    #     logger.info(
    #         f"transaction hash {transaction_hash} generated while registering organization "
    #         f"{org_id} in {self.__env_type} blockchain environment.")
    #     return transaction_hash
    #
    # def __register_organization_in_blockchain(self, org_id, metadata_uri, members):
    #     method_name = "createOrganization"
    #     positional_inputs = (web3.Web3.toHex(text=org_id), hash_to_bytesuri(metadata_uri), members)
    #     transaction_hash = self.__make_trasaction(*positional_inputs, method_name=method_name)
    #     logger.info(
    #         f"transaction hash {transaction_hash} generated while registering organization "
    #         f"{org_id} in {self.__env_type} blockchain environment.")
    #     return transaction_hash

    # def publish_organization_to_test_network(self, organization):
    #     metadata_uri = organization.metadata_ipfs_uri
    #     members = []
    #     org_id = organization.id
    #     if self.__env_type == EnvironmentType.TEST.value:
    #         if self.is_org_published(org_id):
    #             return self.__update_organization_in_blockchain(org_id, metadata_uri)
    #         else:
    #             return self.__register_organization_in_blockchain(org_id, metadata_uri, members)
    #     else:
    #         raise EnvironmentNotFoundException()

    def __service_exist_in_blockchain(self, org_id, service_id, contract, contract_address):
        method_name = "getServiceRegistrationById"
        positional_inputs = (web3.Web3.toHex(text=org_id), web3.Web3.toHex(text=service_id))
        contract = self.__blockchain_util.contract_instance(contract_abi=contract, address=contract_address)
        service_data = self.__blockchain_util.call_contract_function(contract=contract, contract_function=method_name,
                                                                     positional_inputs=positional_inputs)
        logger.info(f"Services :: {service_data}")
        service_found = service_data[0]
        return service_found

    # def update_service_in_blockchain(self, org_id, service_id, metadata_uri):
    #     method_name = "updateServiceRegistration"
    #     positional_inputs = (
    #     web3.Web3.toHex(text=org_id), web3.Web3.toHex(text=service_id), ipfsuri_to_bytesuri(metadata_uri))
    #     transaction_hash = self.__make_trasaction(*positional_inputs, method_name=method_name)
    #     logger.info(f"transaction hash {transaction_hash} generated while "
    #                 f"updating service {service_id} in {self.__env_type} blockchain environment.")
    #     return transaction_hash
    #
    # def register_service_in_blockchain(self, org_id, service_id, metadata_uri):
    #     method_name = "createServiceRegistration"
    #     positional_inputs = (web3.Web3.toHex(text=org_id),
    #                          web3.Web3.toHex(text=service_id),
    #                          ipfsuri_to_bytesuri(metadata_uri))
    #     transaction_hash = self.__make_trasaction(*positional_inputs, method_name=method_name)
    #     logger.info(
    #         f"transaction hash {transaction_hash} generated while registering service {service_id} "
    #         f"in {self.__env_type} blockchain environment.")
    #     return transaction_hash

    def is_service_published(self, org_id, service_id):
        contract = self.__blockchain_util.load_contract(path=self.__contract_path)
        contract_address = self.__blockchain_util.read_contract_address(
            net_id=self.__network_id, path=self.__contract_address_path, key='address')
        return self.__service_exist_in_blockchain(org_id, service_id, contract, contract_address)

    def register_or_update_service_in_blockchain(self, org_id, service_id, metadata_uri):
        if not self.is_org_published(org_id=org_id):
            raise OrganizationNotFoundException()

        if self.is_service_published(org_id=org_id, service_id=service_id):
            transaction_hash = self.update_service_in_blockchain(org_id, service_id, metadata_uri)
        else:
            transaction_hash = self.register_service_in_blockchain(org_id, service_id, metadata_uri)
        return transaction_hash
