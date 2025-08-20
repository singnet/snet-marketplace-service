from datetime import timedelta
from enum import Enum

from deployer.config import CLAIMING_PERIOD_IN_HOURS, BREAK_PERIOD_IN_HOURS, TRANSACTION_TTL_IN_MINUTES


class DaemonStorageType(str, Enum):
    ETCD = "etcd"
    IN_MEMORY = "inmemory"

CLAIMING_PERIOD = timedelta(hours = CLAIMING_PERIOD_IN_HOURS)
BREAK_PERIOD = timedelta(hours = BREAK_PERIOD_IN_HOURS)

AUTH_PARAMETERS = [
    "key",
    "value",
    "location"
]

TRANSACTION_TTL = timedelta(minutes = TRANSACTION_TTL_IN_MINUTES)