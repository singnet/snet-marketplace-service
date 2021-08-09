import os

os.environ["LOG_LEVEL"] = "DEBUG"
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
                             "url": "arn:aws"}],
    "ServiceCreated": [{"name": "", "type": "lambda_arn",
                        "url": "arn:aws"}],

    "ServiceMetadataModified": [{"name": "", "type": "lambda_arn",
                                 "url": "arn:aws:"}],

    "ServiceTagsModified": [{"name": "", "type": "lambda_arn",
                             "url": "arn:aws"}],
    "ServiceDeleted": [{"name": "", "type": "lambda_arn",
                        "url": "arn:aws"}],

    "ChannelOpen": [{"name": "", "type": "lambda_arn",
                     "url": "arn:aws"}],

    "ChannelOpen": [{"name": "", "type": "lambda_arn",
                     "url": "arn:aws"}],
    "ChannelExtend": [{"name": "", "type": "lambda_arn",
                       "url": "arn:aws"}],

    "ChannelAddFunds": [{"name": "", "type": "lambda_arn",
                         "url": "arn:awser"}],
    "ChannelSenderClaim": [{"name": "", "type": "lambda_arn",
                            "url": "arn:aws"}],
    "OpenForStake": [{"name": "", "type": "lambda_arn",
                      "url": "arn:aws"}],
    "SubmitStake": [{"name": "", "type": "lambda_arn",
                     "url": "arn:aws"}],
    "UpdateAutoRenewal": [{"name": "", "type": "lambda_arn",
                           "url": "arn:aws"}],
    "ClaimStake": [{"name": "", "type": "lambda_arn",
                    "url": "arn:aws"}],
    "ApproveStake": [{"name": "", "type": "lambda_arn",
                      "url": "arn:aws"}],
    "RejectStake": [{"name": "", "type": "lambda_arn",
                     "url": "arn:aws"}],
    "AutoRenewStake": [{"name": "", "type": "lambda_arn",
                        "url": "arn:aws"}],
    "RenewStake": [{"name": "", "type": "lambda_arn",
                    "url": "arn:aws"}],
    "WithdrawStake": [{"name": "", "type": "lambda_arn",
                       "url": "arn:aws"}],

}
TRANSACTION_HASH_LIMIT = 20
CONTRACT_BASE_PATH = ""