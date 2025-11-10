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


FREQUENCY_BY_PERIOD = {
    PeriodType.HOUR: "min",
    PeriodType.DAY: "h",
    PeriodType.WEEK: "4h",
    PeriodType.MONTH: "D",
    PeriodType.YEAR: "7D",
    PeriodType.ALL: "30D",
}


class OrderType(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TypeOfMovementOfFunds(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class HaaSServiceStatus(str, Enum):
    # statuses from HaaS
    INIT = "INIT"
    STARTING = "STARTING"
    UP = "UP"
    DOWN = "DOWN"
    ERROR = "ERROR"
    # TODO: add more statuses if needed
