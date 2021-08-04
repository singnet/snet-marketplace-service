from datetime import datetime

from sqlalchemy import Column, VARCHAR, Integer, UniqueConstraint, null, Index
from sqlalchemy.dialects.mysql import TIMESTAMP, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MpeEventsRaw(Base):
    __tablename__ = "mpe_events_raw"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    block_no = Column("block_no", Integer, nullable=False)
    uncle_block_no = Column("uncle_block_no", Integer, nullable=True, default=null)
    event = Column("event", VARCHAR(256), nullable=False)
    event_data = Column("json_str", VARCHAR(256), nullable=True)
    processed = Column("processed", TINYINT, nullable=True, default=null)
    transactionHash = Column("transactionHash", VARCHAR(256), nullable=True, default=null)
    logIndex = Column("logIndex", VARCHAR(256), nullable=True, default=null)
    error_code = Column("error_code", Integer, nullable=True, default=null)
    error_msg = Column("error_msg", VARCHAR(256), nullable=True, default=null)
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(transactionHash, name="uq_mpe_ev")
    Index("blk_no_idx", block_no)


class RfaiEventsRaw(Base):
    __tablename__ = "rfai_events_raw"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    block_no = Column("block_no", Integer, nullable=False)
    uncle_block_no = Column("uncle_block_no", Integer, nullable=True, default=null)
    event = Column("event", VARCHAR(256), nullable=False)
    event_data = Column("json_str", VARCHAR(256), nullable=True)
    processed = Column("processed", TINYINT, nullable=True, default=null)
    transactionHash = Column("transactionHash", VARCHAR(256), nullable=True, default=null)
    logIndex = Column("logIndex", VARCHAR(256), nullable=True, default=null)
    error_code = Column("error_code", Integer, nullable=True, default=null)
    error_msg = Column("error_msg", VARCHAR(256), nullable=True, default=null)
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(transactionHash, name="uq_rf_ev")
    Index("blk_no_idx", block_no)


class EventBlocknumberMarker(Base):
    __tablename__ = "event_blocknumber_marker"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    event_type = Column("event_type", VARCHAR(128), nullable=False)
    last_block_number = Column("last_block_number", Integer, nullable=False)
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())


class TokenStakesEventsRaw(Base):
    __tablename__ = "token_stake_events_raw"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    block_no = Column("block_no", Integer, nullable=False)
    uncle_block_no = Column("uncle_block_no", Integer, nullable=True, default=null)
    event = Column("event", VARCHAR(256), nullable=False)
    event_data = Column("json_str", VARCHAR(256), nullable=True)
    processed = Column("processed", TINYINT, nullable=True, default=null)
    transactionHash = Column("transactionHash", VARCHAR(256), nullable=True, default=null)
    logIndex = Column("logIndex", VARCHAR(256), nullable=True, default=null)
    error_code = Column("error_code", Integer, nullable=True, default=null)
    error_msg = Column("error_msg", VARCHAR(256), nullable=True, default=null)
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(transactionHash, name="uq_st_ev")
    Index("blk_no_idx", block_no)


class RegistryEventsRaw(Base):
    __tablename__ = "registry_events_raw"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    block_no = Column("block_no", Integer, nullable=False)
    uncle_block_no = Column("uncle_block_no", Integer, nullable=True, default=null)
    event = Column("event", VARCHAR(256), nullable=False)
    event_data = Column("json_str", VARCHAR(256), nullable=True)
    processed = Column("processed", TINYINT, nullable=True, default=null)
    transactionHash = Column("transactionHash", VARCHAR(256), nullable=True, default=null)
    logIndex = Column("logIndex", VARCHAR(256), nullable=True, default=null)
    error_code = Column("error_code", Integer, nullable=True, default=null)
    error_msg = Column("error_msg", VARCHAR(256), nullable=True, default=null)
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(transactionHash, name="uq_rg_ev")
    Index("blk_no_idx", block_no)
