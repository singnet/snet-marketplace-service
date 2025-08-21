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

IPFS_URL = {
    'url': 'ipfs.singularitynet.io',
    'port': '80',
}
REGION_NAME = ""

HAAS_BASE_URL = ""
HAAS_LOGIN = ""
HAAS_PASSWORD = ""
HAAS_REGISTRY = ""
HAAS_REG_REPO = ""
HAAS_BASE_IMAGE = ""
HAAS_DAEMON_BASE_URL = ""

START_DAEMON_ARN = ""
DELETE_DAEMON_ARN = ""
UPDATE_DAEMON_STATUS_ARN = ""
REDEPLOY_DAEMON_ARN = ""

DEFAULT_DAEMON_STORAGE_TYPE = DaemonStorageType.ETCD

CLAIMING_PERIOD_IN_HOURS = 0
BREAK_PERIOD_IN_HOURS = 0
TRANSACTION_TTL_IN_MINUTES = 0
DAEMON_STARTING_TTL_IN_MINUTES = 0
DAEMON_RESTARTING_TTL_IN_MINUTES = 0
TRANSFER_TARGET_ADDRESS = ""
HAAS_FIX_PRICE = 0

CONTRACT_BASE_PATH = ""
TOKEN_JSON_FILE_NAME = ""
