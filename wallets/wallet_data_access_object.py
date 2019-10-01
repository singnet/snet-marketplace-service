from datetime import datetime as dt

from common.logger import get_logger

logger = get_logger(__name__)


class WalletDAO:
    def __init__(self, obj_repo):
        self.repo = obj_repo

    def insert_wallet_details(self, username, address, type, status):
        try:
            self.repo.begin_transaction()
            time_now = dt.utcnow()
            wallet_query = "INSERT INTO wallet (address, type, status, row_created, row_updated) VALUES (%s, %s, %s, %s, %s)"
            wallet_query_response = self.repo.execute(wallet_query, [address, type, status, time_now, time_now])

            user_wallet_query = "INSERT INTO user_wallet (username, address, is_default, row_created, row_updated) " \
                                "VALUES (%s, %s, %s, %s, %s)"
            user_wallet_query_response = self.repo.execute(user_wallet_query, [username, address, 1, time_now, time_now])
            if user_wallet_query_response[0] == 1 and wallet_query_response[0] == 1:
                self.repo.commit_transaction()
                return True
            raise Exception("Failed to insert wallet details")
        except Exception as e:
            self.repo.rollback_transaction()
            logger.error(repr(e))
            return False

    def insert_channel_history(self, order_id, amount, currency, type, address, signature, request_parameters,
                               transaction_hash, status):
        params = [order_id, amount, currency, type, address, signature, request_parameters, transaction_hash, status, dt.utcnow(), dt.utcnow()]
        query = "INSERT INTO channel_transaction_history (order_id, amount, currency, type, address, " \
                "signature, request_parameters, transaction_hash, status, row_created, row_updated) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        query_response = self.repo.execute(query, [order_id, amount, currency, type, address, signature,
                                                   request_parameters, transaction_hash, status,
                                                   dt.utcnow(), dt.utcnow()])
        if query_response[0] == 1:
            return True
        return False
