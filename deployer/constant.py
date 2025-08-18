from datetime import timedelta
from enum import Enum


class DaemonStorageType(str, Enum):
    ETCD = "etcd"
    IN_MEMORY = "inmemory"

CLAIMING_PERIOD = timedelta(hours = 1)
BREAK_PERIOD = timedelta(hours = 23)

AUTH_PARAMETERS = [
    "key",
    "value",
    "location"
]