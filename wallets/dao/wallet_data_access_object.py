from datetime import datetime as dt

from common.constant import TransactionStatus
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
            logger.info(f"Insert status for wallet is: {wallet_query_response}")

            is_default = 0
            default_wallet_query = "SELECT * FROM user_wallet WHERE username = %s AND is_default = %s"
            default_wallet = self.repo.execute(default_wallet_query, [username, 1])
            if len(default_wallet) == 0:
                logger.info(f"There is not default wallet for {username}")
                is_default = 1

            user_wallet_query = "INSERT INTO user_wallet (username, address, is_default, row_created, row_updated) " \
                                "VALUES (%s, %s, %s, %s, %s)"
            user_wallet_query_response = self.repo.execute(user_wallet_query,
                                                           [username, address, is_default, time_now, time_now])

            logger.info(f"Insert in user_wallet status is: {user_wallet_query_response}")

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
        query = "SELECT UW.address, UW.is_default, W.type, W.status " \
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

    def get_pending_create_channel_event(self):
        query = "SELECT row_id, payload, status, row_created FROM create_channel_event WHERE status = %s LIMIT 1"
        create_channel_event = self.repo.execute(query, TransactionStatus.PENDING)
        if len(create_channel_event) == 0:
            return None
        return create_channel_event[0]

    def update_create_channel_event(self, event_details, status):
        query = "UPDATE `create_channel_event` SET status = %s WHERE row_id = %s"
        execute_query_result =  self.repo.execute(query, [event_details["row_id"], status])
        if execute_query_result[0] == 1:
            return True
        else:
            return False
