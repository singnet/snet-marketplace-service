from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP, VARCHAR

Base = declarative_base()


class UserVerificationModel(Base):
    __tablename__ = "user_verification"
    transaction_id = Column("transaction_id", VARCHAR(128), primary_key=True)
    user_reference_id = Column("user_reference_id", VARCHAR(128))
    call_back_type = Column("call_back_type", VARCHAR(128))
    jumio_reference = Column("jumio_reference", VARCHAR(128))
    verification_status = Column("verification_status", VARCHAR(128))
    id_scan_status = Column("id_scan_status", VARCHAR(128))
    id_scan_source = Column("id_scan_source", VARCHAR(128))
    transaction_date = Column("transaction_date", TIMESTAMP(timezone=False))
    callback_date = Column("callback_date", TIMESTAMP(timezone=False))
    identity_verification = Column("identity_verification", JSON, default={})
    id_type = Column("id_type", VARCHAR(128))
    error_code = Column("error_code", Integer)
