from datetime import datetime

from sqlalchemy import text, Integer, VARCHAR, TIMESTAMP, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

CreateTimestamp = text("CURRENT_TIMESTAMP")
UpdateTimestamp = text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")


class Base(DeclarativeBase):
    pass


class HostedDaemon(Base):
    __tablename__ = "hosted_daemon"
    id: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    account_id: Mapped[str] = mapped_column("account_id", VARCHAR(128), nullable=False)
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(256), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(256), nullable=False)
    status: Mapped[str] = mapped_column("status", VARCHAR(128), nullable=False)
    from_date: Mapped[datetime] = mapped_column(
        "from_date", TIMESTAMP(timezone = False), nullable = False, server_default = CreateTimestamp
    )
    end_date: Mapped[datetime] = mapped_column(
        "end_date", TIMESTAMP(timezone = False), nullable = False, server_default = CreateTimestamp
    )
    daemon_config: Mapped[dict] = mapped_column("daemon_config", JSON, nullable = False, default = {})

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone = False), nullable = False, server_default = CreateTimestamp
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on",
        TIMESTAMP(timezone = False),
        nullable = False,
        server_default = UpdateTimestamp
    )

