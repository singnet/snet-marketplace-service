from datetime import datetime as dt
from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, BOOLEAN, BINARY, UniqueConstraint
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", VARCHAR(128), nullable=False, unique=True)
    account_id = Column("account_id", VARCHAR(128), nullable=False)
    name = Column("name", VARCHAR(128), nullable=False)
    email = Column("email", VARCHAR(128), nullable=False, unique=True)
    email_verified = Column("email_verified", BINARY, nullable=False, default=b'0')
    email_alerts = Column("email_alerts", BINARY, nullable=False, default=b'0')
    status = Column("status", BINARY, nullable=False, default=b'0')
    request_id = Column("request_id", VARCHAR(128), nullable=False)
    request_time_epoch = Column("request_time_epoch", VARCHAR(128), nullable=False)
    is_terms_accepted = Column("is_terms_accepted", BINARY, nullable=False, default=b'0')
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    preferences = relationship("UserPreference", backref='user', lazy='joined')


class UserPreference(Base):
    __tablename__ = "user_preference"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    user_row_id = Column("user_row_id", Integer,
                         ForeignKey("user.row_id", ondelete="CASCADE", onupdate="CASCADE"),
                         nullable=False)
    preference_type = Column("preference_type", VARCHAR(128), nullable=False)
    communication_type = Column("communication_type", VARCHAR(128), nullable=False)
    source = Column("source", VARCHAR(128), nullable=False)
    opt_out_reason = Column("opt_out_reason", VARCHAR(256), nullable=True)
    status = Column("status", BOOLEAN, nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=dt.utcnow())
    UniqueConstraint(user_row_id, preference_type, communication_type, source, name="user_preference_UN")
