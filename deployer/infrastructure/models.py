from datetime import datetime
from enum import Enum as PythonEnum

from sqlalchemy import text, VARCHAR, TIMESTAMP, JSON, ForeignKey, Enum, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


CreateTimestamp = text("CURRENT_TIMESTAMP")
UpdateTimestamp = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


class Base(DeclarativeBase):
    pass


class DaemonStatus(PythonEnum):
    INIT = "init" # only the entity is created, before payment
    READY_TO_START = "ready_to_start" # paid but not deployed
    STARTING = "starting" # deploying
    DELETING = "deleting" # deleting
    UP = "up" # deployed and working
    # CLAIMING = "claiming"
    DOWN = "down" # not paid
    ERROR_STARTING = "error" # error during deployment
    ERROR_DELETING = "error" # error during deleting
    # DELETED = "deleted"


class OrderStatus(PythonEnum):
    PROCESSING = "processing" # waiting for payment
    SUCCESS = "success" # payment successful
    FAILED = "failed" # payment failed


class EvmTransactionStatus(PythonEnum):
    PENDING = "pending" # transaction pending
    SUCCESS = "success" # transaction successful
    FAILED = "failed" # transaction failed


class ClaimingPeriodStatus(PythonEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Daemon(Base):
    __tablename__ = "daemon"
    id: Mapped[str] = mapped_column("id", VARCHAR(128), primary_key=True)
    account_id: Mapped[str] = mapped_column("account_id", VARCHAR(128), nullable=False)
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(256), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(256), nullable=False)
    status: Mapped[str] = mapped_column(
        "status",
        Enum(DaemonStatus),
        nullable=False,
        default = DaemonStatus.INIT
    )
    start_on: Mapped[datetime] = mapped_column("from_date", TIMESTAMP(timezone = False), nullable = True)
    end_on: Mapped[datetime] = mapped_column("end_date", TIMESTAMP(timezone = False), nullable = True)
    daemon_config: Mapped[dict] = mapped_column("daemon_config", JSON, nullable = False, default = {})

    created_on: Mapped[datetime] = mapped_column(
        "created_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = CreateTimestamp
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = UpdateTimestamp
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        backref = "daemon",
        lazy = "select",
        uselist = True
    )


class Order(Base):
    __tablename__ = "order"
    id: Mapped[str] = mapped_column("id", VARCHAR(128), primary_key=True)
    daemon_id: Mapped[str] = mapped_column(
        "daemon_id",
        VARCHAR(128),
        ForeignKey("daemon.id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable=False,
        index = True
    )
    status: Mapped[OrderStatus] = mapped_column(
        "status",
        Enum(OrderStatus),
        nullable=False,
        default = OrderStatus.PROCESSING
    )

    created_on: Mapped[datetime] = mapped_column(
        "created_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = CreateTimestamp
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = UpdateTimestamp
    )

    evm_transactions: Mapped[list["EVMTransaction"]] = relationship(
        "EVMTransaction",
        backref = "order",
        lazy = "select",
        uselist = True
    )


class EVMTransaction(Base):
    __tablename__ = "evm_transaction"
    hash: Mapped[str] = mapped_column("hash", VARCHAR(128), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        "order_id",
        VARCHAR(128),
        ForeignKey("order.id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable=False,
        index = True
    )
    status: Mapped[EvmTransactionStatus] = mapped_column(
        "status",
        Enum(EvmTransactionStatus),
        nullable=False,
        default = EvmTransactionStatus.PENDING
    )

    created_on: Mapped[datetime] = mapped_column(
        "created_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = CreateTimestamp
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = UpdateTimestamp
    )


class ClaimingPeriod(Base):
    __tablename__ = "claiming_period"
    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    daemon_id: Mapped[str] = mapped_column(
        "daemon_id",
        VARCHAR(128),
        ForeignKey("daemon.id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable=False,
        index = True
    )
    start_on: Mapped[datetime] = mapped_column("start_on", TIMESTAMP(timezone = False), nullable = False)
    end_on: Mapped[datetime] = mapped_column("end_on", TIMESTAMP(timezone = False), nullable = False)
    status: Mapped[ClaimingPeriodStatus] = mapped_column(
        "status",
        Enum(ClaimingPeriodStatus),
        nullable=False,
        default = ClaimingPeriodStatus.INACTIVE
    )

    created_on: Mapped[datetime] = mapped_column(
        "created_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = CreateTimestamp
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = UpdateTimestamp
    )

