from datetime import datetime as dt

from common.constant import TransactionStatus
from common.logger import get_logger

logger = get_logger(__name__)


class WalletDAO:
    def __init__(self, repo):
        self.repo = repo

    def add_user_for_wallet(self, wallet, username):
        is_default = 0
        time_now = dt.utcnow()
        user_wallet_query = "INSERT INTO user_wallet (username, address, is_default, row_created, row_updated) " \
                            "VALUES (%s, %s, %s, %s, %s)"
        user_wallet_query_response = self.repo.execute(user_wallet_query,
                                                       [username, wallet.address, is_default, time_now, time_now])
        logger.info(f"Insert in user_wallet status is: {user_wallet_query_response}")
        if user_wallet_query_response[0] != 1:
            raise Exception("Failed to link user to the wallet")

    def get_wallet_details(self, wallet):
        wallet_query = "SELECT address, type, encrypted_key, status FROM wallet WHERE address = %s"
        wallet_response = self.repo.execute(wallet_query, [wallet.address])
        return wallet_response

    def insert_wallet(self, wallet):
        time_now = dt.utcnow()
        wallet_query = "INSERT INTO wallet (address, type, encrypted_key, status, row_created, row_updated) VALUES (%s, %s, %s, %s, %s, %s)"
        wallet_query_response = self.repo.execute(wallet_query, [wallet.address, wallet.type, wallet.private_key, wallet.status, time_now, time_now])
        logger.info(f"Insert status for wallet is: {wallet_query_response}")
        if wallet_query_response[0] != 1:
            raise Exception("failed to insert the wallet")

    def get_wallet_data_by_username(self, username):
        """ Method to get wallet details for a given username. """
        query = "SELECT UW.address, UW.is_default, W.type, W.encrypted_key, W.status " \
                "FROM user_wallet as UW JOIN wallet as W ON UW.address = W.address WHERE UW.username= %s"
        wallet_data = self.repo.execute(query, username)
        return wallet_data

    def set_default_wallet(self, username, address):
        try:
            is_default = 1
            self.repo.begin_transaction()
            update_default_query_response = self.repo.execute(
                "UPDATE user_wallet SET is_default = %s WHERE username = %s AND address = %s", [is_default, username,
                                                                                                address])
            if update_default_query_response[0] == 1:
                '''Set is_default as 0 for other wallets for given user'''
                is_default = 0
                self.repo.execute("UPDATE user_wallet SET is_default = %s WHERE username = %s AND address <> %s",
                                  [is_default, username, address])
                self.repo.commit_transaction()
            raise Exception("Unable to set default wallet as %s for username %s", address, username)

        except Exception as e:
            self.repo.rollback_transaction()
            print(repr(e))

    def remove_user_wallet(self, username):
        query = "DELETE FROM user_wallet where username=%s"
        self.repo.execute(query, [username])
