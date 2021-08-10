import json
from datetime import datetime as dt

from common.constant import TransactionStatus
from common.logger import get_logger

logger = get_logger(__name__)


class ChannelDAO:

    def __init__(self, repo):
        self.repo = repo

    def get_channel_transactions_for_username_recipient(self, username, org_id, group_id):
        params = [username, group_id, org_id, TransactionStatus.SUCCESS]
        query = "SELECT W.username, W.address, W.type, W.is_default, CT.recipient, CT.amount, " \
                "CT.`type` as transaction_type, CT.currency, CT.status, CT.row_created as created_at " \
                "FROM " \
                "(SELECT UW.username, UW.address, UW.is_default, W.type " \
                "FROM user_wallet as UW JOIN wallet W ON W.address = UW.address " \
                "WHERE UW.username = %s) W " \
                "LEFT JOIN " \
                "(SELECT CT.address, CT.amount, CT.currency, CT.status, CT.recipient, CT.row_created, CT.`type`" \
                "FROM channel_transaction_history as CT " \
                "WHERE CT.group_id = %s AND CT.org_id = %s" \
                "AND  CT.status <> %s) CT " \
                "ON W.address = CT.address"
        channel_data = self.repo.execute(query, params)
        return channel_data

    def insert_channel_history(self, order_id, amount, currency, type, group_id, org_id, recipient,
                               address, signature, request_parameters, transaction_hash, status):
        time_now = dt.now()
        params = [order_id, amount, org_id, group_id, currency, type, recipient, address,
                  signature, request_parameters, transaction_hash, status, time_now, time_now]
        query = "INSERT INTO channel_transaction_history (order_id, amount, org_id, group_id, currency, " \
                "type, recipient, address, signature, request_parameters, " \
                "transaction_hash, status, row_created, row_updated) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        query_response = self.repo.execute(query, params)
        if query_response[0] == 1:
            return True
        return False

    def get_channel_transactions_against_order_id(self, order_id):
        query = "SELECT order_id, amount, currency, type, address, transaction_hash, status, row_created as created_at " \
                "FROM channel_transaction_history WHERE order_id = %s"

        transaction_history = self.repo.execute(query, order_id)
        return transaction_history

    def persist_create_channel_event(self, payload, created_at):
        query = "INSERT INTO create_channel_event (payload, row_created, row_updated, status)" \
                "VALUES (%s, %s, %s, %s)"
        query_response = self.repo.execute(query, [json.dumps(payload), created_at, created_at, TransactionStatus.PENDING])
        if query_response[0] == 1:
            return True
        return False

    def get_one_create_channel_event(self, status):
        query = "SELECT row_id, payload, status, row_created FROM create_channel_event WHERE status = %s LIMIT 1"
        create_channel_event = self.repo.execute(query, status)
        if len(create_channel_event) == 0:
            return None
        return create_channel_event[0]

    def update_create_channel_event(self, event_details, status):
        query = "UPDATE `create_channel_event` SET status = %s WHERE row_id = %s"
        execute_query_result = self.repo.execute(query, [status, event_details["row_id"]])
        if execute_query_result[0] == 1:
            return True
        else:
            return False
