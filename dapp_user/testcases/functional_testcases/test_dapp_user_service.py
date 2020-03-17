import json
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
            'userPoolId': 'us-east-1_vnsxyLKbb',
            'userName': '61ef1036-d2cb-4388-9915-a9289eec973e',
            'callerContext': {
                'awsSdkVersion': 'aws-sdk-unknown-unknown',
                'clientId': '16247r8cm0icg7j1f41gd3k9qh'
            },
            'triggerSource': 'PostConfirmation_ConfirmSignUp',
            'request': {
                'userAttributes': {
                    'sub': '61ef1036-d2cb-4388-9915-a9289eec973e',
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
        response = register_user_post_aws_cognito_signup(event, None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")

    def tearDown(self):
        self._repo.execute("DELETE FROM user")
