from common.logger import get_logger
from orchestrator.dao.transaction_history_data_access_object import TransactionHistoryDAO
from orchestrator.order_status import OrderStatus

logger = get_logger(__name__)


class UpdateTransactionStatus:
    def __init__(self, obj_repo):
        self.transaction_history_data_access_object = TransactionHistoryDAO(obj_repo=obj_repo)

    def manage_update_canceled_order_in_txn_history(self):
        logger.info("Start of UpdateTransactionStatus::manage_update_canceled_order_in_txn_history")
        list_of_order_id_for_expired_transaction = self.transaction_history_data_access_object.get_order_id_for_expired_transaction()
        logger.info(f"List of order_id to be updated with ORDER CANCELED: {list_of_order_id_for_expired_transaction}")
        update_transaction_status = self.transaction_history_data_access_object.update_transaction_status(
            list_of_order_id=list_of_order_id_for_expired_transaction, status=OrderStatus.ORDER_CANCELED.value)
        return True

    def cancel_order_for_given_order_id(self, order_id):
        logger.info("UpdateTransactionStatus::cancel_order_for_given_order_id: %s", order_id)
        update_transaction_status = self.transaction_history_data_access_object.update_transaction_status(
            list_of_order_id=[order_id], status=OrderStatus.ORDER_CANCELED.value)
        return True
