from enum import Enum


class DaemonStorageType(str, Enum):
    ETCD = "etcd"
    IN_MEMORY = "inmemory"


AUTH_PARAMETERS = ["key", "value", "location"]


class AllowedEventNames(str, Enum):
    SERVICE_CREATED = "ServiceCreated"
    SERVICE_METADATA_MODIFIED = "ServiceMetadataModified"
    SERVICE_DELETED = "ServiceDeleted"


class PeriodType(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class HaaSServiceStatus(str, Enum):
    # statuses from HaaS
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESTARTING = "restarting"
    # TODO: Add more statuses
