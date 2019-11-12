from datetime import datetime as dt

from common.logger import get_logger
from orchestrator.config import ORDER_EXPIRATION_THRESHOLD_IN_MINUTES
from orchestrator.order_status import OrderStatus

logger = get_logger(__name__)


class TransactionHistoryDAO:
    def __init__(self, repo):
        self.__repo = repo

    def insert_transaction_history(self, obj_transaction_history):
        transaction_history = obj_transaction_history.get_transaction_history()
        query_response = self.__repo.execute(
            "INSERT INTO transaction_history (username, order_id, order_type, status, payment_id, payment_method, "
            "raw_payment_data, transaction_hash, row_created, row_updated)"
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE payment_id = %s, payment_method = %s, raw_payment_data = %s, transaction_hash = %s, row_updated = %s",
            [
                transaction_history["username"],
                transaction_history["order_id"],
                transaction_history["order_type"],
                transaction_history["status"],
                transaction_history["payment_id"],
                transaction_history["payment_method"],
                transaction_history["raw_payment_data"],
                transaction_history["transaction_hash"],
                dt.utcnow(),
                dt.utcnow(),
                transaction_history["payment_id"],
                transaction_history["payment_method"],
                transaction_history["raw_payment_data"],
                transaction_history["transaction_hash"],
                dt.utcnow()
            ]
        )
        if query_response[0] == 1:
            return True
        return False

    def get_order_id_for_expired_transaction(self):
        params = [OrderStatus.PAYMENT_INITIATED.value, OrderStatus.PAYMENT_INITIATION_FAILED.value,
                  OrderStatus.PAYMENT_EXECUTION_FAILED.value, ORDER_EXPIRATION_THRESHOLD_IN_MINUTES]
        order_id_raw_data = self.__repo.execute(
            "SELECT order_id FROM transaction_history WHERE status IN (%s, %s, %s) AND "
            "TIMESTAMPDIFF(MINUTE, row_created, NOW()) > %s ",
            [OrderStatus.PAYMENT_INITIATED.value, OrderStatus.PAYMENT_INITIATION_FAILED.value,
             OrderStatus.PAYMENT_EXECUTION_FAILED.value, ORDER_EXPIRATION_THRESHOLD_IN_MINUTES])
        list_of_order_id = [rec["order_id"] for rec in order_id_raw_data]
        return list_of_order_id

    def update_transaction_status(self, list_of_order_id, status):
        if len(list_of_order_id) == 0:
            return "No order id found"
        temp_holder = ("%s, " * len(list_of_order_id))[:-2]
        params = [status] + list_of_order_id + [OrderStatus.PAYMENT_INITIATED.value,
                                                OrderStatus.PAYMENT_INITIATION_FAILED.value,
                                                OrderStatus.PAYMENT_EXECUTION_FAILED.value]
        update_transaction_status_response = self.__repo.execute(
            "UPDATE transaction_history SET status = %s WHERE order_id IN (" + temp_holder + ") AND status IN (%s, %s, %s)",
            params)
        logger.info(f"update_transaction_status: {update_transaction_status_response}")
        return update_transaction_status_response

    def get_transaction_details_for_given_order_id(self, order_id):
        transaction_data = self.__repo.execute(
            "SELECT username, order_id, order_type, status, payment_id, payment_type, payment_method, raw_payment_data, "
            "transaction_hash FROM transaction_history WHERE order_id = %s", [order_id])
        if len(transaction_data) == 0:
            raise Exception("Order Id does not exist.")
        return transaction_data[0]
