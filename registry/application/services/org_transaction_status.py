from common import blockchain_util
from common.logger import get_logger
from registry.config import NETWORKS, NETWORK_ID
from registry.constants import OrganizationStatus
from registry.infrastructure.repositories.organization_repository import OrganizationPublisherRepository

logger = get_logger(__name__)


class OrganizationTransactionStatus:
    def __init__(self):
        self.obj_blockchain_util = blockchain_util.BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[NETWORK_ID]["http_provider"]
        )
        self.org_repo = OrganizationPublisherRepository()

    def update_transaction_status(self):
        org_transaction_data = self.org_repo.get_org_state_with_status(OrganizationStatus.PUBLISH_IN_PROGRESS.value)

        failed_org_transactions = []
        for org_state in org_transaction_data:
            transaction_hash = org_state.transaction_hash
            transaction_receipt = self.obj_blockchain_util. \
                get_transaction_receipt_from_blockchain(transaction_hash=transaction_hash)

            if transaction_receipt is None:
                logger.error(f"Failed to get the transaction from blockchain for "
                             f"org:{org_state.org_uuid} hash:{transaction_hash}")
            else:
                if transaction_receipt.status == 0:
                    failed_org_transactions.append(org_state.org_uuid)
                    logger.info(f"Failed service_uuid:{org_state.org_uuid} transaction_hash:{transaction_hash}")

        if len(failed_org_transactions) != 0:
            self.org_repo.update_org_status(
                failed_org_transactions,
                OrganizationStatus.PUBLISH_IN_PROGRESS.value,
                OrganizationStatus.FAILED.value
            )

