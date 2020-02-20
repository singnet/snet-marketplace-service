NETWORKS = {
    3: {
        "name": "test",
        "http_provider": "https://ropsten.infura.io",
        "ws_provider": "wss://ropsten.infura.io/ws",
        "db": {
            "DB_DRIVER": "mysql+pymysql",
            "DB_HOST": "localhost",
            "DB_USER": "unittest_root",
            "DB_PASSWORD": "unittest_pwd",
            "DB_NAME": "user_verification_unittest_db",
            "DB_PORT": 3306,
        },
    }
}
NETWORK_ID = 3
SLACK_HOOK = {}
REGION_NAME = "us-east-2"

JUMIO_API_KEY = "abcde1234!@#$"
JUMIO_BASE_URL = "https://netverify.com/api/v4/"

SUCCESS_REDIRECTION_DAPP_URL = "http://ropsten-publisher.singularitynet.io.s3-website-us-east-1.amazonaws.com/" \
                               "/onboarding/authenticate/individual"
USER_REFERENCE_ID_NAMESPACE = "singularitynet"

