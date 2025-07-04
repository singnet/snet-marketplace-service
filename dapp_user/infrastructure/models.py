from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BOOLEAN,
    DECIMAL,
    VARCHAR,
    BigInteger,
    ForeignKey,
    Integer,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

CreateTimestamp = text("CURRENT_TIMESTAMP")
UpdateTimestamp = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    row_id: Mapped[int] = mapped_column("row_id", BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column("username", VARCHAR(128), nullable=False, unique=True)
    account_id: Mapped[str] = mapped_column("account_id", VARCHAR(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column("name", VARCHAR(128), nullable=False)
    email: Mapped[str] = mapped_column("email", VARCHAR(128), nullable=False, unique=True)
    email_verified: Mapped[bool] = mapped_column(
        "email_verified", BOOLEAN, nullable=False, default=False
    )
    email_alerts: Mapped[bool] = mapped_column(
        "email_alerts", BOOLEAN, nullable=False, default=False
    )
    status: Mapped[bool] = mapped_column("status", BOOLEAN, nullable=False, default=b"0")
    is_terms_accepted: Mapped[bool] = mapped_column(
        "is_terms_accepted", BOOLEAN, nullable=False, default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=CreateTimestamp, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=UpdateTimestamp, nullable=False
    )


class UserPreference(Base):
    __tablename__ = "user_preference"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    user_row_id: Mapped[int] = mapped_column(
        "user_row_id",
        BigInteger,
        ForeignKey(User.row_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    preference_type: Mapped[str] = mapped_column("preference_type", VARCHAR(128), nullable=False)
    communication_type: Mapped[str] = mapped_column(
        "communication_type", VARCHAR(128), nullable=False
    )
    source: Mapped[str] = mapped_column("source", VARCHAR(128), nullable=False)
    opt_out_reason: Mapped[str | None] = mapped_column(
        "opt_out_reason", VARCHAR(256), nullable=True
    )
    status: Mapped[bool] = mapped_column("status", BOOLEAN, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=CreateTimestamp, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=UpdateTimestamp, nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            user_row_id, preference_type, communication_type, source, name="user_preference_unique"
        ),
    )


class UserServiceVote(Base):
    __tablename__ = "user_service_vote"

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_row_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(User.row_id, ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    org_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    rating: Mapped[Decimal] = mapped_column(DECIMAL(2, 1), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=CreateTimestamp, nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=UpdateTimestamp, nullable=True
    )

    __table_args__ = (
        UniqueConstraint(user_row_id, org_id, service_id, name="user_service_vote_unique"),
    )


class UserServiceFeedback(Base):
    __tablename__ = "user_service_feedback"

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_row_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(User.row_id, ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    org_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    comment: Mapped[str] = mapped_column(VARCHAR(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=CreateTimestamp, nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=UpdateTimestamp, nullable=True
    )
