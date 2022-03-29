import os

os.environ["LOG_LEVEL"] = "DEBUG"
LAMBDA_ARN_FORMAT = "arn:aws"
NETWORK_ID = 0
NETWORKS = {
    'name': 'ropsten',
    'http_provider': 'https://ropsten.infura.io/v3/',
    'ws_provider': 'wss://ropsten.infura.io/ws/v3/',
    "db": {
        "HOST": "localhost",
        "USER": "unittest_root",
        "PASSWORD": "unittest_pwd",
        "NAME": "unittest_db",
        "PORT": 3306,
    }
}
DB_DETAILS = {
    "driver": "mysql+pymysql",
    "host": "localhost",
    "user": "unittest_root",
    "password": "unittest_pwd",
    "name": "unittest_db",
    "port": 3306
}
REGION_NAME = "us-east-2"
SLACK_HOOK = {
    'hostname': 'https://hooks.slack.com',
    'port': 443,
    'path': '',
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    }
}
EVENT_SUBSCRIPTIONS = {
    "OrganizationCreated": [{"name": "", "type": "lambda_arn",
                             "url": "arn:aws:lambda:"}],

    "OrganizationModified": [{"name": "", "type": "lambda_arn",
                              "url": "arn:aws:"}],

    "OrganizationDeleted": [{"name": "", "type": "lambda_arn",
                             "url": LAMBDA_ARN_FORMAT}],
    "ServiceCreated": [{"name": "", "type": "lambda_arn",
                        "url": LAMBDA_ARN_FORMAT}],

    "ServiceMetadataModified": [{"name": "", "type": "lambda_arn",
                                 "url": "arn:aws:"}],

    "ServiceTagsModified": [{"name": "", "type": "lambda_arn",
                             "url": LAMBDA_ARN_FORMAT}],
    "ServiceDeleted": [{"name": "", "type": "lambda_arn",
                        "url": LAMBDA_ARN_FORMAT}],

    "ChannelOpen": [{"name": "", "type": "lambda_arn",
                     "url": LAMBDA_ARN_FORMAT}],

    "ChannelOpen": [{"name": "", "type": "lambda_arn",
                     "url": LAMBDA_ARN_FORMAT}],
    "ChannelExtend": [{"name": "", "type": "lambda_arn",
                       "url": LAMBDA_ARN_FORMAT}],

    "ChannelAddFunds": [{"name": "", "type": "lambda_arn",
                         "url": "arn:awser"}],
    "ChannelSenderClaim": [{"name": "", "type": "lambda_arn",
                            "url": LAMBDA_ARN_FORMAT}],
    "OpenForStake": [{"name": "", "type": "lambda_arn",
                      "url": LAMBDA_ARN_FORMAT}],
    "SubmitStake": [{"name": "", "type": "lambda_arn",
                     "url": LAMBDA_ARN_FORMAT}],
    "UpdateAutoRenewal": [{"name": "", "type": "lambda_arn",
                           "url": LAMBDA_ARN_FORMAT}],
    "ClaimStake": [{"name": "", "type": "lambda_arn",
                    "url": LAMBDA_ARN_FORMAT}],
    "ApproveStake": [{"name": "", "type": "lambda_arn",
                      "url": LAMBDA_ARN_FORMAT}],
    "RejectStake": [{"name": "", "type": "lambda_arn",
                     "url": LAMBDA_ARN_FORMAT}],
    "AutoRenewStake": [{"name": "", "type": "lambda_arn",
                        "url": LAMBDA_ARN_FORMAT}],
    "RenewStake": [{"name": "", "type": "lambda_arn",
                    "url": LAMBDA_ARN_FORMAT}],
    "WithdrawStake": [{"name": "", "type": "lambda_arn",
                       "url": LAMBDA_ARN_FORMAT}],
    "Claim": [{"name": "", "type": "lambda_arn",
               "url": LAMBDA_ARN_FORMAT}],
    "ConversionOut": [{"name": "", "type": "lambda_arn",
                       "url": LAMBDA_ARN_FORMAT}],
    "ConversionIn": [{"name": "", "type": "lambda_arn",
                      "url": LAMBDA_ARN_FORMAT}]

}
TRANSACTION_HASH_LIMIT = 20
CONTRACT_BASE_PATH = ""

READ_EVENTS_WITH_BLOCK_DIFFERENCE = 0