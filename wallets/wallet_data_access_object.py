from datetime import datetime as dt

from common.constant import TransactionStatus
from common.logger import get_logger

logger = get_logger(__name__)


class WalletDAO:
    def __init__(self, obj_repo):
        self.repo = obj_repo

    def get_wallet_transactions_for_username_recipient(self, username, recipient):
        params = [username, recipient, TransactionStatus.PENDING, TransactionStatus.FAILED]
        query = "SELECT W.username, W.address, W.is_default, CT.recipient, CT.amount, " \
                "CT.currency, CT.status, CT.row_created as created_at " \
                "FROM " \
                "(SELECT UW.username, UW.address, UW.is_default " \
                "FROM user_wallet as UW JOIN wallet W ON W.address = UW.address " \
                "WHERE UW.username = %s) W " \
                "LEFT JOIN " \
                "(SELECT CT.address, CT.amount, CT.currency, CT.status, CT.recipient, CT.row_created, CT.`type`" \
                "FROM channel_transaction_history as CT " \
                "WHERE CT.recipient = %s " \
                "AND (CT.status = %s OR CT.status = %s) ) CT " \
                "ON W.address = CT.address"
        channel_data = self.repo.execute(query, params)
        return channel_data

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

    def insert_channel_history(self, order_id, amount, currency, type, recipient, address, signature,
                               request_parameters, transaction_hash, status):
        time_now = dt.now()
        params = [order_id, amount, currency, type, recipient, address,
                  signature, request_parameters, transaction_hash, status, time_now, time_now]
        query = "INSERT INTO channel_transaction_history (order_id, amount, currency, " \
                "type, recipient, address, signature, request_parameters, " \
                "transaction_hash, status, row_created, row_updated) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        query_response = self.repo.execute(query, params)
        if query_response[0] == 1:
            return True
        return False

    def get_channel_transactions_against_order_id(self, order_id):
        query = "SELECT order_id, amount, currency, type, address, transaction_hash, row_created as created_at " \
                "FROM channel_transaction_history WHERE order_id = %s"

        transaction_history = self.repo.execute(query, order_id)
        return transaction_history

    def get_wallet_data_by_username(self, username):
        """ Method to get wallet details for a given username. """
        query = "SELECT UW.address, UW.is_default, W.type, W.status " \
                "FROM user_wallet as UW JOIN wallet as W ON UW.address = W.address WHERE UW.username= %s"
        wallet_data = self.repo.execute(query, username)
        return wallet_data
