from datetime import datetime

from sqlalchemy import Column, VARCHAR, Integer, null, UniqueConstraint, JSON
from sqlalchemy.dialects.mssql import BIT
from sqlalchemy.dialects.mysql import TIMESTAMP, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserWallet(Base):
    __tablename__ = "user_wallet"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", VARCHAR(128), nullable=False)
    address = Column("address", VARCHAR(128), nullable=False)
    is_default = Column("is_default", BIT, default=b'0')
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(username, address, name='uq_wallet')


class Wallet(Base):
    __tablename__ = "wallet"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    address = Column("address", VARCHAR(256), nullable=False)
    type = Column("type", VARCHAR(128))
    status = Column("status", BIT, default=b'1')
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(address, address, name='uq_wallet')


class CreateChannelEvent(Base):
    __tablename__ = "create_channel_event"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    payload = Column("payload", JSON, nullable=False)
    status = Column("status", VARCHAR(256), nullable=False)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())


class ChannelTransactionHistory(Base):
    __tablename__ = "channel_transaction_history"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    order_id = Column("order_id", VARCHAR(128), nullable=False)
    amount = Column("amount", Integer, nullable=False)
    currency = Column("currency", VARCHAR(64), nullable=False)
    type = Column("type", VARCHAR(128), nullable=True, default=null)
    address = Column("address", VARCHAR(255), nullable=True, default=null)
    recipient = Column("recipient", VARCHAR(255), nullable=True, default=null)
    signature = Column("signature", VARCHAR(255), nullable=True, default=null)
    org_id = Column("org_id", VARCHAR(255), nullable=True, default=null)
    group_id = Column("group_id", VARCHAR(255), nullable=True, default=null)
    request_parameters = Column("request_parameters", VARCHAR(255), nullable=True, default=null)
    transaction_hash = Column("transaction_hash", VARCHAR(255), nullable=True, default=null)
    status = Column("status", VARCHAR(255), nullable=True, default=null)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
