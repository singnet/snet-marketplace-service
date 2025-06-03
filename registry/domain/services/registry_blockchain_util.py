import web3

from common.blockchain_util import BlockChainUtil
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from registry.config import (
    NETWORK_ID,
    NETWORKS,
    TOKEN_NAME,
    STAGE
)
from registry.constants import EnvironmentType, REG_CNTRCT_PATH, REG_ADDR_PATH
from registry.exceptions import OrganizationNotFoundException

logger = get_logger(__name__)


class RegistryBlockChainUtil:
    def __init__(self, env_type):
        if env_type == EnvironmentType.MAIN.value:
            self.__network_id = NETWORK_ID
            self.__contract_path = REG_CNTRCT_PATH
            self.__contract_address_path = REG_ADDR_PATH
            self.__blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
                                                    provider=NETWORKS[self.__network_id]['http_provider'])
        else:
            raise MethodNotImplemented()

    def is_org_published(self, org_id):
        contract = self.__blockchain_util.load_contract(path=self.__contract_path)
        contract_address = self.__blockchain_util.read_contract_address(
            net_id=self.__network_id,
            path=self.__contract_address_path,
            token_name=TOKEN_NAME,
            stage=STAGE,
            key='address'
        )
        return self.__organization_exist_in_blockchain(org_id, contract, contract_address)

    def __organization_exist_in_blockchain(self, org_id, contract, contract_address):
        method_name = "getOrganizationById"
        positional_inputs = [web3.Web3.to_bytes(text = org_id).ljust(32, b'\0')[:32]]
        contract = self.__blockchain_util.contract_instance(contract_abi=contract, address=contract_address)

        org_data = self.__blockchain_util.call_contract_function(
            contract=contract, contract_function=method_name, positional_inputs=positional_inputs)

        logger.info(f"Org data :: {org_data}")
        org_found = org_data[0]
        return org_found

    def __service_exist_in_blockchain(self, org_id, service_id, contract, contract_address):
        method_name = "getServiceRegistrationById"
        positional_inputs = (web3.Web3.to_hex(text=org_id), web3.Web3.to_hex(text=service_id))
        contract = self.__blockchain_util.contract_instance(contract_abi=contract, address=contract_address)
        service_data = self.__blockchain_util.call_contract_function(contract=contract, contract_function=method_name,
                                                                     positional_inputs=positional_inputs)
        logger.info(f"Services :: {service_data}")
        service_found = service_data[0]
        return service_found

    def is_service_published(self, org_id, service_id):
        contract = self.__blockchain_util.load_contract(path=self.__contract_path)
        contract_address = self.__blockchain_util.read_contract_address(
            net_id = self.__network_id,
            path = self.__contract_address_path,
            token_name = TOKEN_NAME,
            stage = STAGE,
            key = 'address'
        )
        return self.__service_exist_in_blockchain(org_id, service_id, contract, contract_address)

    def register_or_update_service_in_blockchain(self, org_id, service_id, metadata_uri):
        if not self.is_org_published(org_id=org_id):
            raise OrganizationNotFoundException()

        if self.is_service_published(org_id=org_id, service_id=service_id):
            transaction_hash = self.update_service_in_blockchain(org_id, service_id, metadata_uri)
        else:
            transaction_hash = self.register_service_in_blockchain(org_id, service_id, metadata_uri)
        return transaction_hash
