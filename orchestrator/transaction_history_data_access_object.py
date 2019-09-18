class TransactionHistoryDAO():
    def __init__(self, obj_repo):
        self.__repo = obj_repo

    def insert_transaction_history(self, obj_transaction_history):
        transaction_history = obj_transaction_history.get_transaction_history()
        query_response = self.__repo.execute(
            "INSERT INTO transaction_history (username, order_id, order_type, status, payment_id, payment_method, "
            "raw_payment_data, transaction_hash)"
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE_KEY UPDATE payment_id = %s, payment_method = %s, raw_payment_data = %s, transaction_hash = %s",
            [transaction_history["username"], transaction_history["order_id"], transaction_history["order_type"],
             transaction_history["status"], transaction_history["payment_id"], transaction_history["payment_method"],
             transaction_history["raw_payment_data"], transaction_history["transaction_hash"],
             transaction_history["payment_id"], transaction_history["payment_method"],
             transaction_history["raw_payment_data"], transaction_history["transaction_hash"]])
        if query_response[0] == 1:
            return True
        return False
