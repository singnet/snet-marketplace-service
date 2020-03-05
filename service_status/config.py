NETWORKS = {
    0: {
        'name': 'TEST',
        'http_provider': 'https://ropsten.infura.io',
        'ws_provider': 'wss://ropsten.infura.io/ws',
        'db': {'DB_HOST': '127.0.0.1',
               'DB_USER': 'unittest_root',
               'DB_PASSWORD': 'unittest_pwd',
               'DB_NAME': 'unittest_db',
               'DB_PORT': 3306
               }
    } 
}
SLACK_HOOK = {
    'hostname': '',
    'port': 443,
    'path': '',
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    },
    'channel': ''
}
NETWORK_ID = 0
REGION_NAME="us-east-2"
NOTIFICATION_ARN = ""
MAXIMUM_INTERVAL_IN_HOUR = 12
MINIMUM_INTERVAL_IN_HOUR = 1
CERTIFICATION_EXPIRATION_THRESHOLD = 30