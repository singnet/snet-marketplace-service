NETWORKS = {
    0: {
        'name': 'TEST',
        'http_provider': 'https://ropsten.infura.io',
        'ws_provider': 'wss://ropsten.infura.io/ws',
        'db': {'DB_HOST': '127.0.0.1',
               'DB_USER': 'root',
               'DB_PASSWORD': 'root',
               'DB_NAME': 'unittest_db',
               'DB_PORT': 3306
               }
    } 
}
GET_FREE_CALLS_METERING_ARN = ""
PATH_PREFIX = ""
SLACK_HOOK = {
    'hostname': '',
    'port': 443,
    'path': '',
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    }
}
