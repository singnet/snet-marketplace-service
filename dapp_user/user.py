from datetime import datetime as dt

import boto3

from common.constant import PATH_PREFIX
from common.utils import Utils
from schema import Schema, And


class User:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()
        self.ssm_client = boto3.client('ssm', region_name="us-east-1")

    def _set_user_data(self, user_data):
        """ Method to set user information. """
        try:
            claims = user_data['authorizer']['claims']
            email_verified = claims['email_verified']
            status = 0
            if email_verified:
                status = 1
            else:
                raise Exception("Email verification is pending.")
            q_dta = [claims['email'], user_data['accountId'], claims['name'], claims['email'], status,
                     status, user_data['requestId'], user_data['requestTimeEpoch'], dt.utcnow(), dt.utcnow()]
            set_usr_dta = self.repo.execute(
                "INSERT INTO user (username, account_id, name, email, email_verified, status, request_id, "
                "request_time_epoch, row_created, row_updated) "
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", q_dta)
            if len(set_usr_dta) > 0:
                return "success"
            else:
                return "failed"
        except Exception as e:
            print(repr(e))
            raise e


    def get_wallet_details(self, user_data):
        """ Method to get wallet details for a given username. """
        try:
            username = user_data['authorizer']['claims']['email']
            search_data = self.repo.execute("SELECT row_id, address, status FROM wallet WHERE username = %s", username)
            self.obj_utils.clean(search_data)
            return search_data
        except Exception as e:
            print(repr(e))
            raise e

    def _link_wallet(self, username):
        """ Method to assign wallet address to a user. """
        try:
            return self.repo.execute("UPDATE wallet SET username = %s WHERE username is NULL LIMIT 1", username)
        except Exception as e:
            print(repr(e))
            raise e

    def _fetch_private_key_from_ssm(self, address):
        try:
            store = self.ssm_client.get_parameter(
                Name=PATH_PREFIX + str(address), WithDecryption=True)
            return store['Parameter']['Value']
        except Exception as e:
            print(repr(e))
            raise Exception("Error fetching value from parameter store.")

    def user_signup(self, user_data):
        """ Method to assign pre-seeded wallet to user.
            This is one time process.
        """
        try:
            self.repo.begin_transaction()
            username = user_data['authorizer']['claims']['email']
            set_usr_dta = self._set_user_data(user_data)
            if set_usr_dta == "success":
                print(set_usr_dta)
                address_exist = (len(self.get_wallet_details(username=username)) > 0 )
                if address_exist:
                    raise Exception('Useraname is already linked to wallet')
                else:
                    updt_resp = self._link_wallet(username=username)

                    if updt_resp[0] == 1:
                        result = self.repo.execute(
                            "SELECT * FROM wallet where username = %s", username)
                        address = result[0].get("address", None)
                        private_key = self._fetch_private_key_from_ssm(
                            address=address)
                        self.obj_utils.clean(result)
                        result[0].update({"private_key": private_key})
                        self.repo.commit_transaction()
                        return {"success": "success", "data": result}
                    raise Exception("Error in assigning pre-seeded wallet")
            elif set_usr_dta == "failed":
                return "User already exist"
        except Exception as e:
            self.repo.rollback_transaction()
            print(repr(e))
            raise e

    def del_user_data(self, user_data):
        """ Method to delete user data and wallet address.
            Deregister User.
        """
        try:
            username = user_data['authorizer']['claims']['email']
            self.repo.begin_transaction()
            del_user = self.repo.execute(
                "DELETE FROM user WHERE username = %s ", [username])
            updt_wallet = self.repo.execute(
                "UPDATE wallet SET status=0, username=NULL WHERE username = %s ", [username])
            self.repo.commit_transaction()
            return []
        except Exception as e:
            self.repo.rollback_transaction()
            print(repr(e))
            raise e

    def get_user_profile(self, user_data):
        '''
            Method to fetch user profile data.
        '''
        try:
            username = user_data['authorizer']['claims']['email']
            result = self.repo.execute(
                "SELECT * FROM user WHERE username = %s", [username])
            self.obj_utils.clean(result)
            return {"success": "success", "data": result}
        except Exception as e:
            print(repr(e))
            raise e

    def update_user_profile(self, email_alerts, user_data):
        '''
            Method to update user profile data.
        '''
        try:
            username = user_data['authorizer']['claims']['email']
            result = self.repo.execute("UPDATE user SET email_alerts = %s WHERE username = %s", [
                                       int(email_alerts == True), username])
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
            user_address = self._get_user_address_from_username(username=username)
            query_part = ""
            query_part_values = []
            if org_id is not None:
                query_part = "AND org_id = %s "
                query_part_values.append(org_id)
                if service_id is not None:
                    query_part += "AND service_id = %s "
                    query_part_values.append(service_id)

            rating_query = "SELECT * FROM user_service_vote WHERE user_address = %s " + query_part
            rating = self.repo.execute(
                rating_query, [user_address] + query_part_values)
            self.obj_utils.clean(rating)

            feedback_query = "SELECT * FROM user_service_feedback WHERE user_address = %s " + query_part
            feedback = self.repo.execute(
                feedback_query, [user_address] + query_part_values)
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
            user_address = self._get_user_address_from_username(username=username)
            org_id = feedback_data['org_id']
            service_id = feedback_data['service_id']
            comment = feedback_data['comment']
            self.repo.begin_transaction()
            set_rating = "INSERT INTO user_service_vote (user_address, org_id, service_id, rating, row_updated, row_created) " \
                         "VALUES (%s, %s, %s, %s, %s, %s) " \
                         "ON DUPLICATE KEY UPDATE rating = %s, row_updated = %s"
            set_rating_params = [user_address, org_id, service_id,
                                 user_rating, curr_dt, curr_dt, user_rating, curr_dt]
            self.repo.execute(set_rating, set_rating_params)
            set_feedback = "INSERT INTO user_service_feedback (user_address, org_id, service_id, comment, row_updated, row_created)" \
                           "VALUES (%s, %s, %s, %s, %s, %s)"
            set_feedback_params = [user_address, org_id,
                                   service_id, comment, curr_dt, curr_dt]
            self.repo.execute(set_feedback, set_feedback_params)
            self._update_service_rating(org_id=org_id, service_id=service_id)
            self.repo.commit_transaction()
            return True
        except Exception as e:
            self.repo.rollback_transaction()
            print(repr(e))
            raise e

    def _get_user_address_from_username(self, username):
        """
            Method to get user_address for a given username
        """
        try:
            wallet_details = self.repo.execute(
                "SELECT * FROM wallet WHERE username = %s ", [username])
            if len(wallet_details) > 0:
                return wallet_details[0].get("address", None)
            else:
                raise Exception("Wallet address does not exist for this user.")
        except Exception as e:
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
