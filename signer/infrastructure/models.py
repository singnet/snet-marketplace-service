from datetime import datetime

from sqlalchemy import Index, Integer, text
from sqlalchemy.dialects.mysql import TIMESTAMP, VARCHAR, VARBINARY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


CreateTimestamp = text("CURRENT_TIMESTAMP")
UpdateTimestamp = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


class Base(DeclarativeBase):
    pass


class FreeCallToken(Base):
    __tablename__ = "free_call_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    organization_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    group_id: Mapped[str] = mapped_column(VARCHAR(128), nullable=False)
    token: Mapped[bytes] = mapped_column(VARBINARY(512), nullable=False, unique=True)
    expiration_block_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=CreateTimestamp, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=UpdateTimestamp, nullable=False
    )

    __table_args__ = (
        Index("ix_token_body", "username", "organization_id", "service_id", "group_id"),
    )
