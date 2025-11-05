from datetime import timedelta
from enum import Enum


class DaemonStorageType(str, Enum):
    ETCD = "etcd"
    IN_MEMORY = "inmemory"


AUTH_PARAMETERS = ["key", "value", "location"]


class AllowedRegistryEventNames(str, Enum):
    SERVICE_CREATED = "ServiceCreated"
    SERVICE_METADATA_MODIFIED = "ServiceMetadataModified"
    SERVICE_DELETED = "ServiceDeleted"


class PeriodType(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


PERIOD_TYPE_TIMEDELTA = {
    PeriodType.HOUR: timedelta(hours=1),
    PeriodType.DAY: timedelta(days=1),
    PeriodType.WEEK: timedelta(days=7),
    PeriodType.MONTH: timedelta(days=30),
    PeriodType.YEAR: timedelta(days=365),
}


class OrderType(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TypeOfMovementOfFunds(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class HaaSServiceStatus(str, Enum):
    # statuses from HaaS
    STARTING = "starting"
    UP = "up"
    ERROR = "error"
    # TODO: add more statuses if needed
