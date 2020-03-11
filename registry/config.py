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
            "DB_NAME": "registry_unittest_db",
            "DB_PORT": 3306,
        },
    }
}
NETWORK_ID = 3
SLACK_HOOK = {
    'hostname': '',
    'port': 443,
    'path': '',
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    }
}
IPFS_URL = {
    'url': 'ipfs.singularitynet.io',
    'port': '80',

}
ALLOWED_ORIGIN = ["PUBLISHER"]
METADATA_FILE_PATH = "/tmp"
REGION_NAME = "us-east-1"
ASSET_BUCKET = ""
ASSET_DIR = "/tmp"
NOTIFICATION_ARN = ""
PUBLISHER_PORTAL_DAPP_URL = ""
ORG_ID_FOR_TESTING_AI_SERVICE = ""
BLOCKCHAIN_TEST_ENV = {
    "network_id": 3,
    "network_name": "ropsten",
    "executor_address": "",
    "executor_key": "",
    "free_calls": 100
}
SLACK_CHANNEL_FOR_APPROVAL_TEAM = ""
DAEMON_CONFIG_FOR_TEST = {
    "allowed_user_flag": True,
    "allowed_user_addresses": [],
    "blockchain_enabled": False,
    "passthrough_enabled": True,
    "daemon_end_point": "0.0.0.0:XXXX",
    "passthrough_endpoint": "http://localhost:XXXX"
}
DAEMON_CONFIG = {
    "ipfs_end_point": "",
    "blockchain_network_selected": "ropsten",
    "organization_id": None,
    "service_id": None,
    "metering_end_point": "https://ropsten-marketplace.singularitynet.io",
    "authentication_address": None,
    "blockchain_enabled": True
}
