from datetime import datetime
from enum import Enum as PythonEnum

from sqlalchemy import text, VARCHAR, TIMESTAMP, JSON, ForeignKey, Enum, Integer, BOOLEAN, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


CreateTimestamp = text("CURRENT_TIMESTAMP")
UpdateTimestamp = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


class Base(DeclarativeBase):
    pass


class DaemonStatus(PythonEnum):
    INIT = "INIT" # only the entity is created, before payment
    READY_TO_START = "READY_TO_START" # paid but not deployed
    STARTING = "STARTING" # deploying
    RESTARTING = "RESTARTING" # redeploying
    DELETING = "DELETING" # deleting
    UP = "UP" # deployed and working
    # CLAIMING = "claiming"
    DOWN = "DOWN" # not paid
    ERROR = "ERROR" # error during deployment
    # DELETED = "deleted"


class OrderStatus(PythonEnum):
    PROCESSING = "PROCESSING" # waiting for payment
    SUCCESS = "SUCCESS" # payment successful
    FAILED = "FAILED" # payment failed


class EvmTransactionStatus(PythonEnum):
    PENDING = "PENDING" # transaction pending
    SUCCESS = "SUCCESS" # transaction successful
    FAILED = "FAILED" # transaction failed


class ClaimingPeriodStatus(PythonEnum):
    ACTIVE = "ACTIVE" # daemon is deploying and working for the period
    INACTIVE = "INACTIVE" # daemon is deleted and not working
    FAILED = "FAILED" # error during deployment, illegitimate period


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
    service_published: Mapped[bool] = mapped_column(
        "service_published",
        BOOLEAN,
        nullable = False,
        default = False
    )
    daemon_endpoint: Mapped[str] = mapped_column("daemon_endpoint", VARCHAR(256), nullable = False)

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

    __table_args__ = (UniqueConstraint(org_id, service_id, name = "uq_org_srvc"),)


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
    sender: Mapped[str] = mapped_column("sender", VARCHAR(128), nullable=False)
    recipient: Mapped[str] = mapped_column("receiver", VARCHAR(128), nullable=False)

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
    id: Mapped[int] = mapped_column("id", Integer, autoincrement = True, primary_key=True)
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


class TransactionsMetadata:
    __tablename__ = "transactions_metadata"
    id: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    recipient: Mapped[str] = mapped_column("recipient", VARCHAR(128), nullable=False)
    last_block_no: Mapped[int] = mapped_column("last_block_no", Integer, nullable=False)
    fetch_limit: Mapped[int] = mapped_column("fetch_limit", Integer, nullable=False)
    block_adjustment: Mapped[int] = mapped_column("block_adjustment", Integer, nullable=False)

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
