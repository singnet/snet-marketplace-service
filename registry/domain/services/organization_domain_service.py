import web3

from common.blockchain_util import BlockChainUtil
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from common.utils import ipfsuri_to_bytesuri
from registry.config import BLOCKCHAIN_TEST_ENV, NETWORKS, NETWORK_ID
from registry.constants import EnvironmentType, TEST_REG_CNTRCT_PATH, TEST_REG_ADDR_PATH, REG_CNTRCT_PATH, REG_ADDR_PATH

logger = get_logger(__name__)


class OrganizationService:
    def __init__(self):
        self.blockchain_util = BlockChainUtil(provider_type="HTTP_PROVIDER",
                                              provider=NETWORKS[NETWORK_ID]['http_provider'])

    def is_org_published(self, org_id, environment):
        if environment == EnvironmentType.TEST.value:
            contract = self.blockchain_util.load_contract(path=TEST_REG_CNTRCT_PATH)
            contract_address = self.blockchain_util.read_contract_address(net_id=NETWORK_ID, path=TEST_REG_ADDR_PATH,
                                                                          key='address')
        elif environment == EnvironmentType.MAIN.value:
            contract = self.blockchain_util.load_contract(path=REG_CNTRCT_PATH)
            contract_address = self.blockchain_util.read_contract_address(net_id=NETWORK_ID, path=REG_ADDR_PATH,
                                                                          key='address')
        else:
            raise MethodNotImplemented()
        return self.organization_exist_in_blockchain(org_id, contract, contract_address)

    def organization_exist_in_blockchain(self, org_id, contract, contract_address):
        method_name = "getOrganizationById"
        positional_inputs = (web3.Web3.toHex(text=org_id))
        contract = self.blockchain_util.contract_instance(contract_abi=contract, address=contract_address)

        org_data = self.blockchain_util.call_contract_function(contract=contract, contract_function=method_name,
                                                               positional_inputs=positional_inputs)
        logger.info(f"Org data :: {org_data}")
        org_found = org_data[0]
        return org_found

    def generate_blockchain_transaction_for_test_environment(self, *positional_inputs, method_name):
        transaction_object = self.blockchain_util.create_transaction_object(*positional_inputs, method_name=method_name,
                                                                            address=BLOCKCHAIN_TEST_ENV[
                                                                                "executor_address"],
                                                                            contract_path=TEST_REG_CNTRCT_PATH,
                                                                            contract_address_path=TEST_REG_ADDR_PATH,
                                                                            net_id=BLOCKCHAIN_TEST_ENV["network_id"])
        return transaction_object

    def update_organization_in_blockchain(self, org_id, metadata_uri, environment):
        method_name = "changeOrganizationMetadataURI"
        positional_inputs = (web3.Web3.toHex(text=org_id), ipfsuri_to_bytesuri(metadata_uri))
        if environment == EnvironmentType.TEST.value:
            executor_key = BLOCKCHAIN_TEST_ENV["executor_key"]
            transaction_object = self.generate_blockchain_transaction_for_test_environment(
                *positional_inputs, method_name=method_name)
        else:
            logger.info("Environment Not Found.")
            raise MethodNotImplemented()
        raw_transaction = self.blockchain_util.sign_transaction_with_private_key(transaction_object=transaction_object,
                                                                                 private_key=executor_key)
        transaction_hash = self.blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info(
            f"transaction hash {transaction_hash} generated while registering organization "
            f"{org_id} in {environment} blockchain environment.")
        return transaction_hash

    def register_organization_in_blockchain(self, org_id, metadata_uri, members, environment):
        method_name = "createOrganization"
        positional_inputs = (web3.Web3.toHex(text=org_id), ipfsuri_to_bytesuri(metadata_uri), members)
        if environment == EnvironmentType.TEST.value:
            executor_key = BLOCKCHAIN_TEST_ENV["executor_key"]
            transaction_object = self.generate_blockchain_transaction_for_test_environment(
                *positional_inputs, method_name=method_name)
        else:
            logger.info("Environment Not Found.")
            raise MethodNotImplemented()
        raw_transaction = self.blockchain_util.sign_transaction_with_private_key(transaction_object=transaction_object,
                                                                                 private_key=executor_key)
        transaction_hash = self.blockchain_util.process_raw_transaction(raw_transaction=raw_transaction)
        logger.info(
            f"transaction hash {transaction_hash} generated while registering organization "
            f"{org_id} in {environment} blockchain environment.")
        return transaction_hash

    def publish_organization_to_test_network(self, organization):
        metadata_uri = organization.metadata_ipfs_uri
        members = []
        environment = EnvironmentType.TEST.value
        org_id = organization.id
        if self.is_org_published(org_id, environment):
            return self.update_organization_in_blockchain(org_id, metadata_uri, environment)
        else:
            return self.register_organization_in_blockchain(org_id, metadata_uri, members, environment)
