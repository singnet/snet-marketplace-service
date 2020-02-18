from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP, VARCHAR

Base = declarative_base()


class UserVerificationModel(Base):
    __table_name__ = "user_verification"
    call_back_type = Column("call_back_type", VARCHAR(128))
    jumio_id_scan_reference = Column("jumio_id_scan_reference", VARCHAR(128), primary_key=True)
    verification_status = Column("verification_status", VARCHAR(128))
    id_scan_status = Column("id_scan_status", VARCHAR(128))
    id_scan_source = Column("id_scan_source", VARCHAR(128))
    transaction_date = Column("transaction_date", TIMESTAMP(timezone=False))
    callback_date = Column("callback_date", TIMESTAMP(timezone=False))
    identity_verification = Column("identity_verification", JSON, default={})
    id_type = Column("id_type", VARCHAR(128))
