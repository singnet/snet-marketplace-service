from sqlalchemy import Column, Integer, JSON
from sqlalchemy.dialects.mysql import TIMESTAMP, VARCHAR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VerificationModel(Base):
    __tablename__ = "verification"
    id = Column("id", VARCHAR(225), primary_key=True)
    verification_type = Column("verification_type", VARCHAR(225), primary_key=True)
    entity_id = Column("entity_id", VARCHAR(255))
    status = Column("status", VARCHAR(255))
    requestee = Column("requestee", VARCHAR(255))
    reject_reason = Column("reject_reason", VARCHAR(1024))
    created_at = Column("created_at", TIMESTAMP(timezone=False))
    updated_at = Column("updated_at", TIMESTAMP(timezone=False))


class JumioVerificationModel(Base):
    __tablename__ = "jumio_verification"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    verification_id = Column("verification_id", VARCHAR(255))
    username = Column("username", VARCHAR(255))
    jumio_reference_id = Column("jumio_reference_id", VARCHAR(255))
    user_reference_id = Column("user_reference_id", VARCHAR(255))
    redirect_url = Column("redirect_url", VARCHAR(1024))
    transaction_status = Column("transaction_status", VARCHAR(255))
    verification_status = Column("verification_status", VARCHAR(255))
    reject_reason = Column("reject_reason", JSON)
    transaction_date = Column("transaction_date", TIMESTAMP(timezone=False))
    callback_date = Column("callback_date", TIMESTAMP(timezone=False))
    created_at = Column("created_at", TIMESTAMP(timezone=False))


class DUNSVerificationModel(Base):
    __tablename__ = "duns_verification"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    verification_id = Column("verification_id", VARCHAR(255))
    org_uuid = Column("org_uuid", VARCHAR(255))
    comments = Column("comments", JSON, default=[])
    status = Column("status", VARCHAR(255))
    created_at = Column("created_at", TIMESTAMP(timezone=False))
    updated_at = Column("updated_at", TIMESTAMP(timezone=False))
