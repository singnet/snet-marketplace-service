from enum import Enum


class DaemonStorageType(str, Enum):
    ETCD = "etcd"
    IN_MEMORY = "in_memory"

