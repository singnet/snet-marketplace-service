from enum import Enum


class DaemonStorageType(str, Enum):
    ETCD = "etcd"
    IN_MEMORY = "inmemory"


AUTH_PARAMETERS = [
    "key",
    "value",
    "location"
]
