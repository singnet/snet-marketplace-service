from _datetime import datetime as dt
from common.repository import Repository
from dapp_user.config import NETWORK_ID, NETWORKS
from dapp_user.exceptions import UserAlreadyExistException


class UserRepository:
    def __init__(self):
        self._repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    def enable_preference(self, user_preference, user_row_id):
        enable_preference_query = \
            "INSERT INTO user_preference (user_row_id, preference_type, communication_type, source, status, " \
            "created_on, updated_on) " \
            "VALUES(%s, %s, %s, %s, %s, %s, %s) " \
            "ON DUPLICATE KEY UPDATE status = %s, updated_on = %s"
        query_response = self._repo.execute(enable_preference_query,
                                            [user_row_id, user_preference.preference_type,
                                             user_preference.communication_type, user_preference.source,
                                             user_preference.status, dt.utcnow(), dt.utcnow(), user_preference.status,
                                             dt.utcnow()])
        return query_response

    def get_user_data_for_given_username(self, username):
        get_user_data_query = \
            "SELECT row_id, username, account_id, name, email, email_verified, email_alerts, status, request_id, " \
            "request_time_epoch, is_terms_accepted FROM user WHERE username = %s LIMIT 1"
        user_data = self._repo.execute(get_user_data_query, username)
        return user_data

    def disable_preference(self, user_preference, user_row_id):
        disable_preference_query = \
            "UPDATE user_preference SET status = %s, opt_out_reason = %s WHERE user_row_id = %s " \
            "AND preference_type = %s AND communication_type = %s AND source = %s"
        query_response = self._repo.execute(disable_preference_query,
                                            [user_preference.status, user_preference.opt_out_reason, user_row_id,
                                             user_preference.preference_type,
                                             user_preference.communication_type, user_preference.source])
        return query_response

    def get_user_preferences(self, user_row_id):
        get_user_preference = \
            "SELECT status, preference_type, communication_type, source, opt_out_reason FROM user_preference WHERE user_row_id = %s "
        query_response = self._repo.execute(get_user_preference, [user_row_id])
        return query_response

    def delete_user(self, username):
        query = "DELETE FROM user WHERE username = %s "
        self._repo.execute(query, [username])

    def register_user_data(self, user):
        """ register user data """
        user_data = self.get_user_data_for_given_username(username=user.username)
        if bool(user_data):
            raise UserAlreadyExistException()
        query_parameters = [user.email, "", user.origin, user.name, user.email, user.email_verified,
                            user.email_verified, "", "", dt.utcnow(), dt.utcnow()]
        self._repo.execute(
            "INSERT INTO user (username, account_id, origin, name, email, email_verified, status, request_id, "
            "request_time_epoch, row_created, row_updated) "
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", query_parameters)
        return "SUCCESS"
