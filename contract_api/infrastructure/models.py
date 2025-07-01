from datetime import datetime

from sqlalchemy import VARCHAR, Integer, ForeignKey, UniqueConstraint, null, DECIMAL, BIGINT, func, BOOLEAN
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class MpeChannel(Base):
    __tablename__ = "mpe_channel"
    row_id: Mapped[int] = mapped_column("row_id", Integer, autoincrement=True, primary_key=True)
    channel_id: Mapped[int] = mapped_column("channel_id", Integer, nullable=False)
    sender: Mapped[str] = mapped_column("sender", VARCHAR(128), nullable=False)
    signer: Mapped[str] = mapped_column("signer", VARCHAR(256), nullable=False)
    recipient: Mapped[str] = mapped_column("recipient", VARCHAR(128), nullable=False)
    group_id: Mapped[str] = mapped_column("groupId", VARCHAR(128), nullable=False)
    balance_in_cogs: Mapped[int] = mapped_column(
        "balance_in_cogs", DECIMAL(38, 0), default=null
    )
    nonce: Mapped[int] = mapped_column("nonce", Integer, default=null)
    expiration: Mapped[int] = mapped_column("expiration", BIGINT, default=null)
    pending: Mapped[int] = mapped_column("pending", DECIMAL(38, 0), default=null)
    consumed_balance: Mapped[int] = mapped_column(
        "consumed_balance", DECIMAL(38, 0), default=0
    )

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(channel_id, sender, signer, recipient, group_id, name="uq_channel"),
    )


class OrgGroup(Base):
    __tablename__ = "org_group"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(
        "org_id", VARCHAR(128),
        ForeignKey("organization.org_id", ondelete="CASCADE", onupdate = "CASCADE"),
        nullable=False,
        index=True
    )
    group_id: Mapped[str] = mapped_column("group_id", VARCHAR(256), default=null)
    group_name: Mapped[str] = mapped_column("group_name", VARCHAR(128), default=null)
    payment: Mapped[dict] = mapped_column("payment", JSON, default=null)

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(org_id, group_id, name="uq_org_grp"),
    )


class Organization(Base):
    __tablename__ = "organization"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128), nullable=False, unique=True)
    organization_name: Mapped[str] = mapped_column("organization_name", VARCHAR(128), default=null)
    owner_address: Mapped[str] = mapped_column("owner_address", VARCHAR(256), default=null)
    org_metadata_uri: Mapped[str] = mapped_column("org_metadata_uri", VARCHAR(128), default=null)
    org_email: Mapped[str] = mapped_column("org_email", VARCHAR(128), default=null)
    org_assets_url: Mapped[dict] = mapped_column("org_assets_url", JSON, default={})
    is_curated: Mapped[bool]  = mapped_column("is_curated", BOOLEAN, default=null)
    description: Mapped[dict] = mapped_column("description", JSON, default={})
    assets_hash: Mapped[dict] = mapped_column("assets_hash", JSON, default={})
    contacts: Mapped[dict] = mapped_column("contacts", JSON, default={})

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )


class Service(Base):
    __tablename__ = "service"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(
        "org_id", VARCHAR(128),
        ForeignKey("organization.org_id", ondelete="CASCADE", onupdate = "CASCADE"),
        nullable=False,
        index=True
    )
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128), nullable=False)
    service_path: Mapped[str] = mapped_column("service_path", VARCHAR(128), default=null)
    hash_uri: Mapped[str] = mapped_column("hash_uri", VARCHAR(128), default=null)
    is_curated: Mapped[bool] = mapped_column("is_curated", BOOLEAN, default=null)
    service_email: Mapped[str] = mapped_column("service_email", VARCHAR(128), default=null)

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )

    service_metadata = relationship("ServiceMetadata", uselist=False)

    __table_args__ = (
        UniqueConstraint(org_id, service_id, name = "uq_srvc"),
    )


class ServiceEndpoint(Base):
    __tablename__ = "service_endpoint"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id: Mapped[int] = mapped_column(
        "service_row_id", Integer,
        ForeignKey("service.row_id", ondelete="CASCADE", onupdate = "CASCADE"),
        nullable=False,
        index=True
    )
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128), nullable=False)
    group_id: Mapped[str] = mapped_column("group_id", VARCHAR(256), nullable=False)
    endpoint: Mapped[str] = mapped_column("endpoint", VARCHAR(256), default=null)
    is_available: Mapped[bool] = mapped_column("is_available", BOOLEAN, default=null)
    last_check_timestamp: Mapped[datetime] = mapped_column(
        "last_check_timestamp", TIMESTAMP(timezone=False), nullable=True, default=null
    )
    next_check_timestamp: Mapped[datetime] = mapped_column(
        "next_check_timestamp", TIMESTAMP(timezone=False), nullable=True, server_default=func.now()
    )
    failed_status_count: Mapped[int] = mapped_column("failed_status_count", Integer, default=1)

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )


class ServiceGroup(Base):
    __tablename__ = "service_group"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id: Mapped[int] = mapped_column(
        "service_row_id", Integer,
        ForeignKey("service.row_id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable = False,
        index = True
    )
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128), nullable=False)
    free_call_signer_address: Mapped[str] = mapped_column(
        "free_call_signer_address", VARCHAR(256), default=null
    )
    free_calls: Mapped[int] = mapped_column("free_calls", Integer, default=null)
    group_id: Mapped[str] = mapped_column("group_id", VARCHAR(256), nullable=False)
    group_name: Mapped[str] = mapped_column("group_name", VARCHAR(128), nullable=False)
    pricing: Mapped[dict] = mapped_column("pricing", JSON, default={})

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(org_id, service_id, group_id, name = "uq_srvc_grp"),
    )


class ServiceMedia(Base):
    __tablename__ = "service_media"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id: Mapped[int] = mapped_column(
        "service_row_id", Integer,
        ForeignKey("service.row_id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable = False,
        index = True
    )
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128), nullable=False)
    url: Mapped[str] = mapped_column("url", VARCHAR(512), default=null)
    order: Mapped[int] = mapped_column("order", Integer, default=null)
    file_type: Mapped[str] = mapped_column("file_type", VARCHAR(128), default=null)
    asset_type: Mapped[str] = mapped_column("asset_type", VARCHAR(128), default=null)
    alt_text: Mapped[str] = mapped_column("alt_text", VARCHAR(128), default=null)
    hash_uri: Mapped[str] = mapped_column("hash_uri", VARCHAR(512), default=null)
    
    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )


class ServiceMetadata(Base):
    __tablename__ = "service_metadata"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id: Mapped[int] = mapped_column(
        "service_row_id", Integer,
        ForeignKey("service.row_id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable = False,
        index = True
    )
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128), nullable=False)
    display_name: Mapped[str] = mapped_column("display_name", VARCHAR(256), default=null)
    description: Mapped[str] = mapped_column("description", VARCHAR(1024), default=null)
    short_description: Mapped[str] = mapped_column("short_description", VARCHAR(1024), default=null)
    demo_component_available: Mapped[bool] = mapped_column(
        "demo_component_available", BOOLEAN, default=0, server_default="0", nullable=False
    )
    url: Mapped[str] = mapped_column("url", VARCHAR(256), default=null)
    json: Mapped[str] = mapped_column("json", VARCHAR(1024), default=null)
    model_hash: Mapped[str] = mapped_column("model_hash", VARCHAR(256), default=null)
    encoding: Mapped[str] = mapped_column("encoding", VARCHAR(128), default=null)
    type: Mapped[str] = mapped_column("type", VARCHAR(128), default=null)
    mpe_address: Mapped[str] = mapped_column("mpe_address", VARCHAR(256), default=null)
    assets_url: Mapped[dict] = mapped_column("assets_url", JSON, default={})
    assets_hash: Mapped[dict] = mapped_column("assets_hash", JSON, default={})
    service_rating: Mapped[dict] = mapped_column("service_rating", JSON, default={})
    ranking: Mapped[int]  = mapped_column("ranking", Integer, default=1)
    contributors: Mapped[dict] = mapped_column("contributors", JSON, default={})

    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(org_id, service_id, name = "uq_srvc_mdata"),
    )


class ServiceTags(Base):
    __tablename__ = "service_tags"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id: Mapped[int] = mapped_column(
        "service_row_id", Integer,
        ForeignKey("service.row_id", ondelete = "CASCADE", onupdate = "CASCADE"),
        nullable = False,
        index = True
    )
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128), default=null)
    tag_name: Mapped[str] = mapped_column("tag_name", VARCHAR(128), default=null)
    
    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    __table_args__ = (
        UniqueConstraint(org_id, service_id, tag_name, name = "uq_srvc_tag"),
    )


class OffchainServiceConfig(Base):
    __tablename__ = "offchain_service_config"
    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128), nullable=False)
    parameter_name: Mapped[str] = mapped_column("parameter_name", VARCHAR(128), nullable=False)
    parameter_value: Mapped[str] = mapped_column("parameter_value", VARCHAR(512), nullable=False)
    
    created_on: Mapped[datetime] = mapped_column(
        "created_on", TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        "updated_on", 
        TIMESTAMP(timezone=False), 
        nullable=False, 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    __table_args__ = (
        UniqueConstraint(org_id, service_id, parameter_name, name="uq_off"),
    )
