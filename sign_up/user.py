from datetime import datetime as dt

import boto3

from common.constant import PATH_PREFIX
from common.utils import Utils


class User:
    def __init__(self, obj_repo):
        self.repo = obj_repo
        self.obj_utils = Utils()
        self.ssm_client = boto3.client('ssm', region_name="us-east-1")

    def set_user_info(self, user_data):
        """ Method to set user information. """
        try:
            claims = user_data['authorizer']['claims']
            email_verified = claims['email_verified']
            status = 0
            if email_verified:
                status = 1
            else:
                raise Exception("Email verification is pending.")
            q_dta = [claims['cognito:username'], user_data['accountId'], claims['name'], claims['email'], status,
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

    def check_for_existing_wallet(self, username):
        """ Method to check for existing wallet address. """
        try:
            srch_dta = self.repo.execute(
                "SELECT * FROM wallet WHERE username = %s", username)
            search_data = self.repo.execute(
                "SELECT count(*) FROM wallet WHERE username = %s", username)
            if srch_dta == []:
                print('Username not found')
                return False
            return True
        except Exception as e:
            print(repr(e))
            raise e

    def update_wallet(self, username):
        """ Method to assign wallet address to a user. """
        try:
            return self.repo.execute("UPDATE wallet SET username = %s WHERE username is NULL LIMIT 1", username)
        except Exception as e:
            print(repr(e))
            raise e

    def fetch_private_key_from_ssm(self, address):
        try:
            store = self.ssm_client.get_parameter(Name=PATH_PREFIX + str(address), WithDecryption=True)
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
            username = user_data['authorizer']['claims']['cognito:username']
            set_usr_dta = self.set_user_info(user_data)
            if set_usr_dta == "success":
                print(set_usr_dta)
                address_exist = self.check_for_existing_wallet(
                    username=username)
                if address_exist:
                    raise Exception('Useraname is already linked to wallet')
                else:
                    updt_resp = self.update_wallet(username=username)

                    if updt_resp[0] == 1:
                        result = self.repo.execute("SELECT * FROM wallet where username = %s", username)
                        address = result[0].get("address", None)
                        private_key = self.fetch_private_key_from_ssm(address=address)
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
            username = user_data['authorizer']['claims']['cognito:username']
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
            username = user_data['authorizer']['claims']['cognito:username']
            result = self.repo.execute("SELECT * FROM user WHERE username = %s", [username])
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
            username = user_data['authorizer']['claims']['cognito:username']
            result = self.repo.execute("UPDATE user SET email_alerts = %s WHERE username = %s", [int(email_alerts==True), username])
            return {"success": "success", "data": []}
        except Exception as e:
            print(repr(e))
            raise e
