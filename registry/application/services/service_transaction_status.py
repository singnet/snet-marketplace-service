from web3.exceptions import TransactionNotFound

from common import blockchain_util
from common.logger import get_logger
from registry.config import NETWORKS, NETWORK_ID
from registry.constants import ServiceStatus
from registry.infrastructure.repositories.service_publisher_repository import (
    ServicePublisherRepository,
)

logger = get_logger(__name__)
service_repo = ServicePublisherRepository()


class ServiceTransactionStatus:
    def __init__(self):
        self.obj_blockchain_util = blockchain_util.BlockChainUtil(
            provider_type="HTTP_PROVIDER", provider=NETWORKS[NETWORK_ID]["http_provider"]
        )

    def update_transaction_status(self):
        states = service_repo.get_service_state(ServiceStatus.PUBLISH_IN_PROGRESS.value)
        failed_service_transactions = []

        for state in states:
            try:
                transaction_receipt = (
                    self.obj_blockchain_util.get_transaction_receipt_from_blockchain(
                        transaction_hash=state.transaction_hash
                    )
                )
            except TransactionNotFound:
                logger.info(
                    f"Transaction not found service_uuid:{state.service_uuid} transaction_hash:{state.transaction_hash}"
                )
                failed_service_transactions.append(state.service_uuid)
                continue

            if transaction_receipt is None or transaction_receipt.status == 0:
                failed_service_transactions.append(state.service_uuid)
                logger.info(
                    f"Failed service_uuid:{state.service_uuid} transaction_hash:{state.transaction_hash}"
                )

        if len(failed_service_transactions) > 0:
            service_repo.update_service_status(
                failed_service_transactions,
                ServiceStatus.PUBLISH_IN_PROGRESS.value,
                ServiceStatus.FAILED.value,
            )
