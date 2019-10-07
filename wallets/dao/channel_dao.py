from datetime import datetime as dt

from common.constant import TransactionStatus
from common.logger import get_logger

logger = get_logger(__name__)


class ChannelDAO:
    def __init__(self, obj_repo):
        self.repo = obj_repo

    def get_channel_transactions_for_username_recipient(self, username, recipient):
        params = [
            username,
            recipient,
            TransactionStatus.FAILED,
            TransactionStatus.PENDING,
        ]
        query = (
            "SELECT W.username, W.address, W.is_default, CT.recipient, CT.amount, "
            "CT.currency, CT.status, CT.row_created as created_at "
            "FROM "
            "(SELECT UW.username, UW.address, UW.is_default "
            "FROM user_wallet as UW JOIN wallet W ON W.address = UW.address "
            "WHERE UW.username = %s) W "
            "LEFT JOIN "
            "(SELECT CT.address, CT.amount, CT.currency, CT.status, CT.recipient, CT.row_created, CT.`type`"
            "FROM channel_transaction_history as CT "
            "WHERE CT.recipient = %s "
            "AND (CT.status = %s OR CT.status = %s)) CT "
            "ON W.address = CT.address"
        )
        channel_data = self.repo.execute(query, params)
        return channel_data

    def insert_channel_history(
        self,
        order_id,
        amount,
        currency,
        type,
        recipient,
        address,
        signature,
        request_parameters,
        transaction_hash,
        status,
    ):
        time_now = dt.now()
        params = [
            order_id,
            amount,
            currency,
            type,
            recipient,
            address,
            signature,
            request_parameters,
            transaction_hash,
            status,
            time_now,
            time_now,
        ]
        query = (
            "INSERT INTO channel_transaction_history (order_id, amount, currency, "
            "type, recipient, address, signature, request_parameters, "
            "transaction_hash, status, row_created, row_updated) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        query_response = self.repo.execute(query, params)
        if query_response[0] == 1:
            return True
        return False

    def get_channel_transactions_against_order_id(self, order_id):
        query = (
            "SELECT order_id, amount, currency, type, address, transaction_hash, row_created as created_at "
            "FROM channel_transaction_history WHERE order_id = %s"
        )

        transaction_history = self.repo.execute(query, order_id)
        return transaction_history
