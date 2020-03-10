import web3

from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from registry.config import BLOCKCHAIN_TEST_ENV
from registry.constants import EnvironmentType, TEST_REG_CNTRCT_PATH, TEST_REG_ADDR_PATH

logger = get_logger(__name__)


class OrganizationService:
    def __init__(self, blockchain_util):
        self.blockchain_util = blockchain_util

    def generate_blockchain_transaction_for_test_environment(self, *positional_inputs, method_name):
        transaction_object = self.blockchain_util.create_transaction_object(*positional_inputs, method_name=method_name,
                                                                            address=BLOCKCHAIN_TEST_ENV[
                                                                                "executor_address"],
                                                                            contract_path=TEST_REG_CNTRCT_PATH,
                                                                            contract_address_path=TEST_REG_ADDR_PATH,
                                                                            net_id=BLOCKCHAIN_TEST_ENV["network_id"])
        return transaction_object

    def register_organization_in_blockchain(self, org_id, metadata_uri, members, environment):
        method_name = "createOrganization"
        positional_inputs = (web3.Web3.toHex(text=org_id), metadata_uri, members)
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
            f"transaction hash {transaction_hash} generated while registering organization {org_id} in {environment} blockchain "
            f"environment.")
