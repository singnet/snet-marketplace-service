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
            wallet_query_response = self.repo.execute(
                wallet_query, [address, type, status, time_now, time_now]
            )

            is_default = 0
            default_wallet_query = (
                "SELECT * FROM user_wallet WHERE username = %s AND is_default = %s"
            )
            default_wallet = self.repo.execute(default_wallet_query, [username, 1])
            if len(default_wallet) == 0:
                is_default = 1

            user_wallet_query = (
                "INSERT INTO user_wallet (username, address, is_default, row_created, row_updated) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            user_wallet_query_response = self.repo.execute(
                user_wallet_query, [username, address, is_default, time_now, time_now]
            )
            if user_wallet_query_response[0] == 1 and wallet_query_response[0] == 1:
                self.repo.commit_transaction()
                return True
            raise Exception("Failed to insert wallet details")
        except Exception as e:
            self.repo.rollback_transaction()
            logger.error(repr(e))
            return False

    def get_wallet_data_by_username(self, username):
        """ Method to get wallet details for a given username. """
        query = (
            "SELECT UW.address, UW.is_default, W.type, W.status "
            "FROM user_wallet as UW JOIN wallet as W ON UW.address = W.address WHERE UW.username= %s"
        )
        wallet_data = self.repo.execute(query, username)
        return wallet_data
