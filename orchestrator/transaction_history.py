class TransactionHistory:
    def __init__(
            self,
            username,
            order_id,
            order_type,
            status,
            payment_id="",
            payment_method="",
            raw_payment_data="{}",
            transaction_hash=""
    ):
        self.__username = username
        self.__order_id = order_id
        self.__order_type = order_type
        self.__status = status
        self.__payment_id = payment_id
        self.__payment_method = payment_method
        self.__raw_payment_data = raw_payment_data
        self.__transaction_hash = transaction_hash

    def get_transaction_history(self):
        return {
            "username": self.__username,
            "order_id": self.__order_id,
            "order_type": self.__order_type,
            "status": self.__status,
            "payment_id": self.__payment_id,
            "payment_method": self.__payment_method,
            "raw_payment_data": self.__raw_payment_data,
            "transaction_hash": self.__transaction_hash
        }
