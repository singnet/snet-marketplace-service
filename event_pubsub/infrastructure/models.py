from datetime import datetime

from sqlalchemy import Column, VARCHAR, Integer, UniqueConstraint, null, text
from sqlalchemy.dialects.mysql import TIMESTAMP, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MpeEventsRaw(Base):
    __tablename__ = "mpe_events_raw"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    block_no = Column("block_no", Integer, nullable=False)
    event = Column("event", VARCHAR(256), nullable=False)
    json_str = Column("json_str", VARCHAR(256), nullable=False)
    processed = Column("processed", TINYINT, nullable=True, default=null)
    transactionHash = Column("transactionHash", VARCHAR(256), nullable=True, default=null)
    logIndex = Column("logIndex", VARCHAR(256), nullable=True, default=null)
    error_code = Column("error_code", Integer, nullable=True, default=null)
    error_msg = Column("error_msg", VARCHAR(256), nullable=True, default=null)
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(block_no, transactionHash, name="uq_mpe_ev")
