import json
from unittest import TestCase
from dapp_user.lambda_handler import request_handler
from common.repository import Repository
from dapp_user.config import NETWORK_ID, NETWORKS


class TestUserSignUp(TestCase):
    def setUp(self):
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    def test_user_signup(self):
        self.tearDown()
        event = {
            "resource": "/signup",
            "path": "/dapp-user/signup",
            "httpMethod": "GET",
            "headers": {
                "Authorization": "",
                "Host": "ropsten-marketplace.singularitynet.io",
                "origin": "https://beta.singularitynet.io",
                "referer": "https://beta.singularitynet.io/aimarketplace",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            },
            "multiValueHeaders": {},
            "queryStringParameters": {"origin": "PUBLISHER_DAPP"},
            "multiValueQueryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "resourceId": "kduff6",
                "authorizer": {
                    "claims": {
                        "sub": "00af3833-47ce-4b3c-b2f9-af09440dac30",
                        "aud": "2ddk0m23u0ovju2fst34q0t96j",
                        "email_verified": "true",
                        "event_id": "7bb22434-626d-483d-8519-7275d61fdbae",
                        "token_use": "id",
                        "auth_time": "1583996248",
                        "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_fVrm4ARvK",
                        "nickname": "Ankit",
                        "cognito:username": "00af3833-47ce-4b3c-b2f9-af09440dac30",
                        "exp": "Thu Mar 12 07:57:31 UTC 2020",
                        "iat": "Thu Mar 12 06:57:31 UTC 2020",
                        "email": "ankitm@grr.la"
                    }
                },
                "resourcePath": "/signup",
                "httpMethod": "GET",
                "extendedRequestId": "JQ-GlEIfIAMF9xw=",
                "requestTime": "12/Mar/2020:06:57:33 +0000",
                "path": "/dapp-user/signup",
                "accountId": "533793137436",
                "protocol": "HTTP/1.1",
                "stage": "mainnet",
                "domainPrefix": "mainnet-marketplace",
                "requestTimeEpoch": 1583996253283,
                "requestId": "0c543e73-343a-4d6f-9cbf-5ad1d5de6ec7",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": None,
                    "cognitoIdentityId": None,
                    "caller": None,
                    "sourceIp": "111.93.235.50",
                    "principalOrgId": None,
                    "accessKey": None,
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": None,
                    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
                    "user": None
                },
                "domainName": "ropsten-marketplace.singularitynet.io",
                "apiId": "6nfct1u0yf"
            },
            "isBase64Encoded": False
        }
        response = request_handler(event=event, context=None)
        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        record_count = self.repo.execute("SELECT * FROM user")
        assert(len(record_count) == 1)

    def tearDown(self):
        self.repo.execute("DELETE FROM user")
