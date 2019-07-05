from datetime import datetime as dt


class User:
    def __init__(self, obj_repo):
        self.repo = obj_repo

    def set_user_info(self, usr_dta):
        """ Method to set user information. """
        try:
            claims = usr_dta['authorizer']['claims']
            email_verified = claims['email_verified']
            status = 0
            if email_verified:
                status = 1
            else:
                raise Exception("Email Verification is pending.")
            q_dta = [claims['cognito:username'], usr_dta['accountId'], claims['name'], claims['email'], status,
                     status, usr_dta['requestId'], usr_dta['requestTimeEpoch'], dt.utcnow(), dt.utcnow()]
            set_usr_dta = self.repo.execute(
                "INSERT INTO user (username, account_id, name, email, email_verified, status, request_id, "
                "request_time_epoch, row_created, row_updated) "
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", q_dta)
            if len(set_usr_dta) > 0:
                return True
            else:
                return False
        except Exception as e:
            print(repr(e))
            raise e

    def check_for_existing_address(self, username):
        """ Method to check for existing wallet address. """
        try:
            srch_dta = self.repo.execute(
                "SELECT * FROM wallet WHERE username = %s", username)
            if srch_dta == []:
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

    def user_signup(self, usr_dta):
        """ Method to assign pre-seeded wallet to user.
            This is one time process.
        """
        try:
            self.repo.begin_transaction()
            username = usr_dta['authorizer']['claims']['cognito:username']
            set_usr_dta = self.set_user_info(usr_dta)
            if set_usr_dta:
                address_exist = self.check_for_existing_address(
                    username=username)
                if address_exist:
                    raise Exception('Useraname is already linked to wallet.')
                else:
                    updt_resp = self.update_wallet(username=username)

                if updt_resp[0] == 1:
                    self.repo.commit_transaction()
                    result = self.repo.execute(
                        "SELECT * FROM wallet WHERE username = %s", username)
                    self.repo.execute(
                        "UPDATE wallet SET private_key = NULL WHERE username = %s", [username])
                    return {"success": "success", "data": result}
                return None
            else:
                raise Exception("User Already Exist!")

        except Exception as e:
            self.repo.rollback_transaction()
            print(repr(e))
            raise e

    def del_user_data(self, username):
        """ Method to delete user data and wallet address.
            Deregister User.
        """
        try:
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
