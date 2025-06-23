from unittest import TestCase
from dapp_user.application.handlers.user_handlers import register_user_post_aws_cognito_signup
from common.repository import Repository
from dapp_user.config import NETWORK_ID, NETWORKS


class DappUserService(TestCase):
    def setUp(self):
        self._repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    def test_register_user_on_post_cognito_signup(self):
        event = {
            'version': '1',
            'region': 'us-east-2',
            'userPoolId': 'us-east-2 tyuiop',
            'userName': '12345-d2cb-6789-9915-45678',
            'callerContext': {
                'awsSdkVersion': 'aws-sdk-unknown-unknown',
                'clientId': 'dummy_client_id_1'
            },
            'triggerSource': 'PostConfirmation_ConfirmSignUp',
            'request': {
                'userAttributes': {
                    'sub': '23456789-d2cb-4388-9915-3456789',
                    'cognito:email_alias': 'piyush@grr.la',
                    'cognito:user_status': 'CONFIRMED',
                    'email_verified': 'true',
                    'nickname': 'Piyush',
                    'email': 'piyush@grr.la'
                }
            },
            'response': {
            }
        }
        event_response = register_user_post_aws_cognito_signup(event, None)
        assert (event_response == event)

    def tearDown(self):
        self._repo.execute("DELETE FROM user")
