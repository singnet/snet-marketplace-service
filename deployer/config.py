from deployer.constant import DaemonStorageType

NETWORKS = {
    11155111: {
        "name": "test",
        "http_provider": "https://sepolia.infura.io",
        "ws_provider": "wss://sepolia.infura.io/ws",
        "db": {
            "DB_DRIVER": "mysql+pymysql",
            "DB_HOST": "localhost",
            "DB_USER": "unittest_root",
            "DB_PASSWORD": "unittest_pwd",
            "DB_NAME": "deployer_unittest_db",
            "DB_PORT": 3306,
        },
    }
}
NETWORK_ID = 11155111
TOKEN_NAME = "FET"
STAGE = "dev"
TOKEN_DECIMALS = 18

IPFS_URL = {
    "url": "ipfs.singularitynet.io",
    "port": "80",
}
REGION_NAME = ""

HAAS_BASE_URL = ""
HAAS_LOGIN = ""
HAAS_PASSWORD = ""
HAAS_REGISTRY = ""
HAAS_REG_REPO = ""
HAAS_DAEMON_IMAGE = ""
HAAS_DAEMON_BASE_URL = ""

HAAS_DEPLOY_DAEMON_PATH = ""
HAAS_DELETE_DAEMON_PATH = ""
HAAS_GET_DAEMON_LOGS_PATH = ""
HAAS_GET_PUBLIC_KEY_PATH = ""
HAAS_DELETE_HOSTED_SERVICE_PATH = ""
HAAS_GET_HOSTED_SERVICE_LOGS_PATH = ""
HAAS_GET_CALL_EVENTS_PATH = ""

START_DAEMON_ARN = ""
GET_ALL_ORGS_ARN = ""

DEPLOY_SERVICE_TOPIC_ARN = ""

DEFAULT_DAEMON_STORAGE_TYPE = DaemonStorageType.ETCD

TRANSACTION_TTL_IN_MINUTES = 0

JWT_EXPIRATION_IN_MINUTES = 0
GITHUB_APP_ID = ""
GITHUB_PRIVATE_KEY = """
"""

REQUEST_MAX_LIMIT = 0

CONTRACT_BASE_PATH = ""
TOKEN_JSON_FILE_NAME = ""
