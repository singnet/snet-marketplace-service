from datetime import datetime
from enum import Enum as PythonEnum
from typing import List

from sqlalchemy import (
    text,
    VARCHAR,
    TIMESTAMP,
    JSON,
    ForeignKey,
    Enum,
    Integer,
    UniqueConstraint,
    DECIMAL,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


CreateTimestamp = text("CURRENT_TIMESTAMP")
UpdateTimestamp = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


class Base(DeclarativeBase):
    pass


class DeploymentStatus(PythonEnum):
    INIT = "INIT"  # only the entity is created during the onboarding
    STARTING = "STARTING"  # deploying is in progress
    UP = "UP"  # deployed and working
    DOWN = "DOWN"  # the service is deleted from blockchain
    ERROR = "ERROR"  # error during deployment


class OrderStatus(PythonEnum):
    INIT = "INIT"  # only the entity is created, waiting for payment
    PROCESSING = "PROCESSING"  # waiting for confirmation
    SUCCESS = "SUCCESS"  # payment successful
    FAILED = "FAILED"  # payment failed
    CANCELLED = "CANCELLED"


class EVMTransactionStatus(PythonEnum):
    PENDING = "PENDING"  # transaction pending
    SUCCESS = "SUCCESS"  # transaction successful
    FAILED = "FAILED"  # transaction failed


class AccountBalance(Base):
    __tablename__ = "account_balance"
    account_id: Mapped[str] = mapped_column("account_id", VARCHAR(128), primary_key=True)
    balance_in_cogs: Mapped[int] = mapped_column("balance", DECIMAL(38, 0), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP(timezone = False), nullable = False, server_default = CreateTimestamp
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", TIMESTAMP(timezone = False), nullable = False, server_default = UpdateTimestamp
    )


class Daemon(Base):
    __tablename__ = "daemon"
    id: Mapped[str] = mapped_column("id", VARCHAR(128), primary_key=True)
    account_id: Mapped[str] = mapped_column(
        "account_id",
        VARCHAR(128),
        ForeignKey("account_balance.account_id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable = False,
        index = True,
    )
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(256), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(256), nullable=False)
    status: Mapped[str] = mapped_column(
        "status", Enum(DeploymentStatus), nullable=False, default=DeploymentStatus.INIT
    )
    daemon_config: Mapped[dict] = mapped_column("daemon_config", JSON, nullable=False, default={})
    daemon_endpoint: Mapped[str] = mapped_column("daemon_endpoint", VARCHAR(256), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP(timezone=False), nullable=False, server_default=CreateTimestamp
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", TIMESTAMP(timezone=False), nullable=False, server_default=UpdateTimestamp
    )

    __table_args__ = (UniqueConstraint(org_id, service_id, name="uq_org_srvc"),)


class HostedService(Base):
    __tablename__ = "hosted_service"
    id: Mapped[str] = mapped_column("id", VARCHAR(128), primary_key = True)
    daemon_id: Mapped[str] = mapped_column(
        "daemon_id",
        VARCHAR(128),
        ForeignKey("daemon.id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable = False,
        index = True,
    )
    status: Mapped[str] = mapped_column(
        "status", Enum(DeploymentStatus), nullable = False, default = DeploymentStatus.INIT
    )
    github_url: Mapped[str] = mapped_column("github_url", VARCHAR(256), nullable = False)
    last_commit_url: Mapped[str] = mapped_column("last_commit_url", VARCHAR(256), nullable = False)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP(timezone = False), nullable = False, server_default = CreateTimestamp
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", TIMESTAMP(timezone = False), nullable = False, server_default = UpdateTimestamp
    )

    __table_args__ = (UniqueConstraint(daemon_id, name = "uq_daemon"),)


class Order(Base):
    __tablename__ = "order"
    id: Mapped[str] = mapped_column("id", VARCHAR(128), primary_key=True)
    account_id: Mapped[str] = mapped_column(
        "account_id",
        VARCHAR(128),
        ForeignKey("account_balance.account_id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable = False,
        index = True,
    )
    status: Mapped[OrderStatus] = mapped_column(
        "status", Enum(OrderStatus), nullable=False, default=OrderStatus.PROCESSING
    )
    amount: Mapped[int] = mapped_column("amount", DECIMAL(38, 0), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP(timezone=False), nullable=False, server_default=CreateTimestamp
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", TIMESTAMP(timezone=False), nullable=False, server_default=UpdateTimestamp
    )

    evm_transactions: Mapped[List["EVMTransaction"]] = relationship(
        "EVMTransaction", backref="order", lazy="select", uselist=True
    )


class EVMTransaction(Base):
    __tablename__ = "evm_transaction"
    hash: Mapped[str] = mapped_column("hash", VARCHAR(128), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        "order_id",
        VARCHAR(128),
        ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[EVMTransactionStatus] = mapped_column(
        "status", Enum(EVMTransactionStatus), nullable=False, default=EVMTransactionStatus.PENDING
    )
    sender: Mapped[str] = mapped_column("sender", VARCHAR(128), nullable=False)
    recipient: Mapped[str] = mapped_column("recipient", VARCHAR(128), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP(timezone=False), nullable=False, server_default=CreateTimestamp
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", TIMESTAMP(timezone=False), nullable=False, server_default=UpdateTimestamp
    )


class TransactionsMetadata(Base):
    __tablename__ = "transactions_metadata"
    id: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    recipient: Mapped[str] = mapped_column("recipient", VARCHAR(128), nullable=False)
    last_block_no: Mapped[int] = mapped_column("last_block_no", Integer, nullable=False)
    fetch_limit: Mapped[int] = mapped_column("fetch_limit", Integer, nullable=False)
    block_adjustment: Mapped[int] = mapped_column("block_adjustment", Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP(timezone=False), nullable=False, server_default=CreateTimestamp
    )
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", TIMESTAMP(timezone=False), nullable=False, server_default=UpdateTimestamp
    )
