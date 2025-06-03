from datetime import datetime as dt

from schema import Schema, And

from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import Utils
from dapp_user.config import PATH_PREFIX, REGION_NAME

DEFAULT_WALLET_TYPE = "METAMASK"
CREATED_BY = "snet"

logger = get_logger(__name__)


class User:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()
        self.boto_client = BotoUtils(region_name=REGION_NAME)

    def _set_user_data(self, user_data, origin):
        """ Method to set user information. """
        try:
            claims = user_data['authorizer']['claims']
            email_verified = claims['email_verified']
            status = 0
            if email_verified:
                status = 1
            else:
                raise Exception("Email verification is pending.")
            q_dta = [claims['email'], user_data['accountId'], origin, claims['nickname'], claims['email'], status,
                     status, user_data['requestId'], user_data['requestTimeEpoch'], dt.utcnow(), dt.utcnow()]
            set_usr_dta = self.repo.execute(
                "INSERT INTO user (username, account_id, origin, name, email, email_verified, status, request_id, "
                "request_time_epoch, row_created, row_updated) "
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", q_dta)
            if len(set_usr_dta) > 0:
                return "success"
            else:
                return "User already exist"
        except Exception as e:
            print(repr(e))
            raise e

    def _fetch_private_key_from_ssm(self, address):
        try:
            store = self.boto_client.get_ssm_parameter(parameter=PATH_PREFIX + str(address))
            return store['Parameter']['Value']
        except Exception as e:
            print(repr(e))
            raise Exception("Error fetching value from parameter store.")

    def user_signup(self, user_data, origin):
        """ Method to assign pre-seeded wallet to user.
            This is one time process.
        """
        try:
            username = user_data['authorizer']['claims']['email']
            set_user_data = self._set_user_data(user_data, origin)
            print(set_user_data)
            return set_user_data
        except Exception as e:
            self.repo.rollback_transaction()
            print(repr(e))
            raise e

    def get_user_profile(self, user_data):
        """
            Method to fetch user profile data.
        """
        try:
            username = user_data['authorizer']['claims']['email']
            result = self.repo.execute(
                "SELECT * FROM user WHERE username = %s", [username])
            self.obj_utils.clean(result)
            return {"success": "success", "data": result}
        except Exception as e:
            print(repr(e))
            raise e

    def update_user_profile(self, email_alerts, is_terms_accepted, user_data):
        """
            Method to update user profile data.
        """
        try:
            username = user_data['authorizer']['claims']['email']
            result = self.repo.execute("UPDATE user SET email_alerts = %s, is_terms_accepted = %s WHERE username = %s",
                                       [int(email_alerts is True), int(is_terms_accepted is True), username])
            return {"success": "success", "data": []}
        except Exception as e:
            print(repr(e))
            raise e

    def validate_and_set_user_feedback(self, feedback_data, user_data):
        """
            Method to validate and set user feedback data.
        """
        schema = Schema([{'org_id': And(str),
                          'service_id': And(str),
                          'user_rating': And(str),
                          'comment': And(str)
                          }])
        try:
            feedback_data = schema.validate([feedback_data])
            feedback_recorded = self._set_user_feedback(
                feedback_data[0], user_data=user_data)
            if feedback_recorded:
                return []
            return None
        except Exception as err:
            print("Invalid Input ", err)
            return None

    def get_user_feedback(self, user_data, org_id, service_id):
        """
            Method to get user feedback data.
        """
        try:
            user_rating_dict = {}
            username = user_data['authorizer']['claims']['email']
            query_part = ""
            query_part_values = []
            if org_id is not None:
                query_part = "AND org_id = %s "
                query_part_values.append(org_id)
                if service_id is not None:
                    query_part += "AND service_id = %s "
                    query_part_values.append(service_id)

            rating_query = "SELECT * FROM user_service_vote WHERE username = %s " + query_part
            rating = self.repo.execute(
                rating_query, [username] + query_part_values)
            self.obj_utils.clean(rating)

            feedback_query = "SELECT * FROM user_service_feedback WHERE username = %s " + query_part
            feedback = self.repo.execute(
                feedback_query, [username] + query_part_values)
            self.obj_utils.clean(feedback)

            for record in feedback:
                org_id = record['org_id']
                service_id = record['service_id']
                if org_id not in user_rating_dict.keys():
                    user_rating_dict[org_id] = {}
                if service_id not in user_rating_dict.keys():
                    user_rating_dict[org_id][service_id] = {}
                    user_rating_dict[org_id][service_id]['comment'] = []
                user_rating_dict[org_id][service_id]['comment'].append(
                    record['comment'])

            for record in rating:
                org_id = record['org_id']
                service_id = record['service_id']
                record.update({'comment': user_rating_dict.get(org_id, {})
                              .get(service_id, {})
                              .get("comment", [])})
            return rating
        except Exception as e:
            print(repr(e))
            raise e

    def _set_user_feedback(self, feedback_data, user_data):
        """
            Method to set user rating and feedback.
        """
        try:
            user_rating = str(feedback_data['user_rating'])
            if float(user_rating) > 5.0 or float(user_rating) < 1.0:
                raise Exception(
                    "Invalid Rating. Provided user rating should be between 1.0 and 5.0 .")
            curr_dt = dt.utcnow()
            username = user_data['authorizer']['claims']['email']
            org_id = feedback_data['org_id']
            service_id = feedback_data['service_id']
            comment = feedback_data['comment']
            self.repo.begin_transaction()
            set_rating = "INSERT INTO user_service_vote (username, org_id, service_id, rating, row_updated, row_created) " \
                         "VALUES (%s, %s, %s, %s, %s, %s) " \
                         "ON DUPLICATE KEY UPDATE rating = %s, row_updated = %s"
            set_rating_params = [username, org_id, service_id,
                                 user_rating, curr_dt, curr_dt, user_rating, curr_dt]
            self.repo.execute(set_rating, set_rating_params)
            set_feedback = "INSERT INTO user_service_feedback (username, org_id, service_id, comment, row_updated, row_created)" \
                           "VALUES (%s, %s, %s, %s, %s, %s)"
            set_feedback_params = [username, org_id,
                                   service_id, comment, curr_dt, curr_dt]
            self.repo.execute(set_feedback, set_feedback_params)
            self._update_service_rating(org_id=org_id, service_id=service_id)
            self.repo.commit_transaction()
            return True
        except Exception as e:
            self.repo.rollback_transaction()
            print(repr(e))
            raise e

    def _update_service_rating(self, org_id, service_id):
        """
            Method updates service_rating and total_user_rated when user rating is changed for given service_id
            and org_id.
        """
        try:
            update_service_metadata = self.repo.execute(
                "UPDATE service_metadata A  INNER JOIN (SELECT U.org_id, U.service_id, AVG(U.rating) AS service_rating, "
                "count(*) AS total_users_rated FROM user_service_vote AS U WHERE U.rating IS NOT NULL GROUP BY "
                "U.service_id, U.org_id ) AS B ON A.org_id=B.org_id AND A.service_id=B.service_id SET A.service_rating "
                "= CONCAT('{\"rating\":', B.service_rating, ' , \"total_users_rated\":', B.total_users_rated, '}') "
                "WHERE A.org_id = %s AND A.service_id = %s ", [org_id, service_id])
        except Exception as e:
            print(repr(e))
            raise e