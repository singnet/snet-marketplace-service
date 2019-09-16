from datetime import datetime as dt


class WalletDAO:
    def __init__(self, obj_repo):
        self.repo = obj_repo

    def insert_wallet_details(self, address, type, status):
        query = "INSERT INTO wallet (address, type, status, row_created, row_updated) VALUES (%s, %s, %s, %s, %s)"
        query_response = self.repo.execute(
            query, [address, type, status, dt.utcnow(), dt.utcnow()]
        )
        if query_response[0] == 1:
            return True
        return False

    def insert_channel_history(
        self,
        order_id,
        amount,
        currency,
        type,
        address,
        signature,
        request_parameters,
        transaction_hash,
        status,
    ):
        query = (
            "INSERT INTO channel_transaction_history (order_id, amount, currency, type, address, "
            "signature, request_parameters, transaction_type, transaction_hash, status, row_created, row_updated) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        query_response = self.repo.execute(
            query,
            [
                order_id,
                amount,
                currency,
                type,
                address,
                signature,
                request_parameters,
                transaction_hash,
                status,
                dt.utcnow(),
                dt.utcnow(),
            ],
        )
        if query_response[0] == 1:
            return True
        return False
