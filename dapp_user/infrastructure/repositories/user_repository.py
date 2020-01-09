from _datetime import datetime as dt
from common.repository import Repository
from dapp_user.config import NETWORK_ID, NETWORKS


class UserRepository:
    def __init__(self):
        self._repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    def enable_preference(self, user_preference, user_row_id):
        query_response = self._repo.execute(
            "INSERT INTO user_preference (user_row_id, preference_type, communication_type, source, status, "
            "created_on, updated_on) "
            "VALUES(%s, %s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE status = %s, updated_on = %s",
            [user_row_id, user_preference.preference_type, user_preference.communication_type, user_preference.source,
             user_preference.status, dt.utcnow(), dt.utcnow(), user_preference.status, dt.utcnow()])
        return query_response

    def get_user_data_for_given_username(self, username):
        user_data = self._repo.execute(
            "SELECT row_id, username, account_id, name, email, email_verified, email_alerts, status, request_id, "
            "request_time_epoch, is_terms_accepted FROM user WHERE username = %s LIMIT 1", username)
        return user_data

    def disable_preference(self, user_preference, user_row_id):
        query_response = self._repo.execute(
            "UPDATE user_preference SET status = %s, opt_out_reason = %s WHERE user_row_id = %s AND preference_type = %s "
            "AND communication_type = %s AND source = %s",
            [user_preference.status, user_preference.opt_out_reason, user_row_id, user_preference.preference_type,
             user_preference.communication_type, user_preference.source])
        return query_response
