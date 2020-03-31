from unittest.mock import Mock

import web3
from common.blockchain_util import BlockChainUtil
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from common.utils import ipfsuri_to_bytesuri
from registry.config import BLOCKCHAIN_TEST_ENV, NETWORKS, NETWORK_ID
from registry.constants import EnvironmentType, TEST_REG_CNTRCT_PATH, TEST_REG_ADDR_PATH, REG_CNTRCT_PATH, REG_ADDR_PATH

logger = get_logger(__name__)


class OrganizationBlockChainUtil:
    def __init__(self, env_type):
        self.__env_type = env_type
        if env_type == EnvironmentType.MAIN.value:
            self.__network_id = NETWORK_ID
            self.__contract_path = REG_CNTRCT_PATH
            self.__contract_address_path = REG_ADDR_PATH
            self.__blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
                                                    provider=NETWORKS[self.__network_id]['http_provider'])

        elif env_type == EnvironmentType.TEST.value:
            self.__contract_path = TEST_REG_CNTRCT_PATH
            self.__contract_address_path = TEST_REG_ADDR_PATH
            self.__network_id = BLOCKCHAIN_TEST_ENV["network_id"]
            self.__blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
                                                    provider=BLOCKCHAIN_TEST_ENV['http_provider'])
        else:
            raise MethodNotImplemented()

    def is_org_published(self, org_id):
        contract = self.__blockchain_util.load_contract(path=TEST_REG_CNTRCT_PATH)
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

    def __generate_blockchain_transaction_for_test_environment(self, *positional_inputs, method_name):
        transaction_object = self.__blockchain_util.create_transaction_object(
            *positional_inputs, method_name=method_name, address=BLOCKCHAIN_TEST_ENV["executor_address"],
            contract_path=self.__contract_path, contract_address_path=self.__contract_address_path,
            net_id=BLOCKCHAIN_TEST_ENV["network_id"])
        return transaction_object

    def __update_organization_in_blockchain(self, org_id, metadata_uri):
        method_name = "changeOrganizationMetadataURI"
        positional_inputs = (web3.Web3.toHex(text=org_id), ipfsuri_to_bytesuri(metadata_uri))
        if self.__env_type == EnvironmentType.TEST.value:
            executor_key = BLOCKCHAIN_TEST_ENV["executor_key"]
            transaction_object = self.__generate_blockchain_transaction_for_test_environment(
                *positional_inputs, method_name=method_name)
        else:
            logger.info("Environment Not Found.")
            raise MethodNotImplemented()
        raw_transaction = self.__blockchain_util.sign_transaction_with_private_key(
            transaction_object=transaction_object,
            private_key=executor_key)
        transaction_hash = self.__blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info(
            f"transaction hash {transaction_hash} generated while registering organization "
            f"{org_id} in {self.__env_type} blockchain environment.")
        return transaction_hash

    def __register_organization_in_blockchain(self, org_id, metadata_uri, members):
        method_name = "createOrganization"
        positional_inputs = (web3.Web3.toHex(text=org_id), ipfsuri_to_bytesuri(metadata_uri), members)
        if self.__env_type == EnvironmentType.TEST.value:
            executor_key = BLOCKCHAIN_TEST_ENV["executor_key"]
            transaction_object = self.__generate_blockchain_transaction_for_test_environment(
                *positional_inputs, method_name=method_name)
        else:
            logger.info("Environment Not Found.")
            raise MethodNotImplemented()
        raw_transaction = self.__blockchain_util.sign_transaction_with_private_key(
            transaction_object=transaction_object,
            private_key=executor_key)
        transaction_hash = self.__blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info(
            f"transaction hash {transaction_hash} generated while registering organization "
            f"{org_id} in {self.__env_type} blockchain environment.")
        return transaction_hash
    def publish_organization_to_test_network(self, organization):

        metadata_uri = organization.metadata_ipfs_uri
        members = []
        org_id = organization.id
        if self.__env_type == EnvironmentType.TEST.value:
            if self.is_org_published(org_id):
                return self.__update_organization_in_blockchain(org_id, metadata_uri)
            else:
                return self.__register_organization_in_blockchain(org_id, metadata_uri, members)
        else:
            raise MethodNotImplemented()
