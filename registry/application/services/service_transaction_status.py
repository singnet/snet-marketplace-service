from common import blockchain_util
from common.logger import get_logger
from registry.config import NETWORKS, NETWORK_ID
from registry.constants import ServiceStatus
from registry.infrastructure.repositories.service_publisher_repository import ServicePublisherRepository

logger = get_logger(__name__)
service_repo = ServicePublisherRepository()


class ServiceTransactionStatus:
    def __init__(self):
        self.obj_blockchain_util = blockchain_util.BlockChainUtil(provider_type="HTTP_PROVIDER",
                                                                  provider=NETWORKS[NETWORK_ID]['http_provider'])

    def update_transaction_status(self):
        org_transaction_data = service_repo.get_service_state_with_status(ServiceStatus.PUBLISH_IN_PROGRESS.value)
        failed_service_transactions = []
        for service_state in org_transaction_data:
            service_uuid = service_state.service_uuid
            transaction_hash = service_state.transaction_hash
            transaction_receipt = self.obj_blockchain_util.get_transaction_receipt_from_blockchain(
                transaction_hash=transaction_hash)
            if transaction_receipt is None:
                pass
            else:
                if transaction_receipt.status == 0:
                    failed_service_transactions.append(service_uuid)
                    logger.info(f"Failed service_uuid:{service_uuid} transaction_hash:{transaction_hash}")
        if len(failed_service_transactions) > 0:
            service_repo.update_service_status(failed_service_transactions, ServiceStatus.PUBLISH_IN_PROGRESS.value, ServiceStatus.FAILED.value)
