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