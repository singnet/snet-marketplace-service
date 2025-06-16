NETWORKS = {
    3: {
        "name": "test",
        "http_provider": "https://ropsten.infura.io",
        "ws_provider": "wss://ropsten.infura.io/ws",
    }
}
NETWORK_ID = 3
SLACK_HOOK = {
    'hostname': '',
    'path': ''
}
REGION_NAME = ""
UPLOAD_BUCKET = {
    "FEEDBACK_BUCKET": "",
    "ORG_BUCKET": ""
}
ALLOWED_CONTENT_TYPE = ["application/zip", "application/x-tar", "image/jpg", "image/jpeg", "image/png", "application/x-zip-compressed"]
FILE_EXTENSION = {"application/zip": 'zip', "image/jpg": "jpg", "image/jpeg": "jpeg", "image/png": "png", "application/x-tar": "tar", "application/x-zip-compressed": "zip"}
SLACK_FEEDBACK_HOOK = {
    "MARKETPLACE": "",
    "RFAI": "",
    "STAKING": ""
}
CRYPTO_FIAT_CONVERSION = {
    'EXCHANGE': 'COINMARKETCAP',
    'RATE_THRESHOLD': 0,
    'MULTIPLIER': '1',
    'CURRENT_AGI_USD_RATE': '3',
    'LIMIT': '10',
    'COINMARKETCAP': {
        'API_ENDPOINT': 'https://'
    }
}
SUPPORTED_ENVIRONMENT = []
PROTO_DIRECTORY_REGEX_PATTERN = ""
NODEJS_PROTO_LAMBDA_ARN = ""
PYTHON_PROTO_LAMBDA_ARN = ""
NETWORK_NAME = ""
