from datetime import datetime

from sqlalchemy import Integer, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP, VARCHAR, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organization"

    uuid: Mapped[str] = mapped_column("uuid", VARCHAR(128), primary_key=True)
    name: Mapped[str] = mapped_column("name", VARCHAR(128))
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128))
    org_type: Mapped[str] = mapped_column("org_type", VARCHAR(128))
    origin: Mapped[str] = mapped_column("origin", VARCHAR(128))
    description: Mapped[str] = mapped_column("description", VARCHAR(1024))
    short_description: Mapped[str] = mapped_column("short_description", VARCHAR(1024))
    url: Mapped[str] = mapped_column("url", VARCHAR(512))
    duns_no: Mapped[str] = mapped_column("duns_no", VARCHAR(36))
    contacts: Mapped[str] = mapped_column("contacts", JSON, nullable=False)
    assets: Mapped[str] = mapped_column("assets", JSON, nullable=False)
    metadata_uri: Mapped[str] = mapped_column("metadata_uri", VARCHAR(255))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    org_state = relationship("OrganizationState", backref='organization', lazy='joined')
    groups = relationship("Group", backref='organization', lazy='joined')
    addresses = relationship("OrganizationAddress", backref='organization', lazy='joined')


class OrganizationAddress(Base):
    __tablename__ = "organization_address"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid: Mapped[str] = mapped_column(
        "org_uuid",
        VARCHAR(128),
        ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    address_type: Mapped[str] = mapped_column("address_type", VARCHAR(64))
    street_address: Mapped[str] = mapped_column("street_address", VARCHAR(256))
    apartment: Mapped[str] = mapped_column("apartment", VARCHAR(256))
    city: Mapped[str] = mapped_column("city", VARCHAR(64))
    pincode: Mapped[str] = mapped_column("pincode", VARCHAR(64))
    state: Mapped[str] = mapped_column("state", VARCHAR(64))
    country: Mapped[str] = mapped_column("country", VARCHAR(64))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class OrganizationState(Base):
    __tablename__ = "organization_state"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid: Mapped[str] = mapped_column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    state: Mapped[str] = mapped_column("state", VARCHAR(128), nullable=False)
    transaction_hash: Mapped[str] = mapped_column("transaction_hash", VARCHAR(128))
    nonce: Mapped[int] = mapped_column("nonce", Integer)
    test_transaction_hash: Mapped[str] = mapped_column("test_transaction_hash", VARCHAR(128))
    wallet_address: Mapped[str] = mapped_column("user_address", VARCHAR(128))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    updated_by: Mapped[str] = mapped_column("updated_by", VARCHAR(128), nullable=False)
    updated_on: Mapped[str] = mapped_column("updated_on", TIMESTAMP(timezone=False))
    reviewed_by: Mapped[str] = mapped_column("approved_by", VARCHAR(128))
    reviewed_on: Mapped[datetime] = mapped_column("approved_on", TIMESTAMP(timezone=False))
    comments: Mapped[dict] = mapped_column("comments", JSON, default=[])


class OrganizationMember(Base):
    __tablename__ = "org_member"

    row_id: Mapped[int] = mapped_column("row_id", Integer, autoincrement=True, primary_key=True)
    invite_code: Mapped[str] = mapped_column("invite_code", VARCHAR(128))
    org_uuid: Mapped[str] = mapped_column(
        "org_uuid",
        VARCHAR(128),
        ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    role: Mapped[str] = mapped_column("role", VARCHAR(128))
    username: Mapped[str] = mapped_column("username", VARCHAR(128))
    address: Mapped[str] = mapped_column("address", VARCHAR(128))
    status: Mapped[str] = mapped_column("status", VARCHAR(128))
    transaction_hash: Mapped[str] = mapped_column("transaction_hash", VARCHAR(128))
    invited_on = mapped_column("invited_on", TIMESTAMP(timezone=False))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Group(Base):
    __tablename__ = "group"

    row_id: Mapped[int] = mapped_column("row_id", Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column("name", VARCHAR(128), nullable=False)
    id: Mapped[str] = mapped_column("id", VARCHAR(128), nullable=False)
    org_uuid: Mapped[str] = mapped_column(
        "org_uuid",
        VARCHAR(128),
        ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    payment_address: Mapped[str] = mapped_column("payment_address", VARCHAR(128))
    payment_config: Mapped[dict] = mapped_column("payment_config", JSON, nullable=False)
    status: Mapped[str] = mapped_column("status", VARCHAR(128))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class OrganizationArchive(Base):
    __tablename__ = "organization_archive"

    row_id: Mapped[int] = mapped_column("row_id", Integer, autoincrement=True, primary_key=True)
    uuid: Mapped[str] = mapped_column("uuid", VARCHAR(128))
    name: Mapped[str] = mapped_column("name", VARCHAR(128))
    org_id: Mapped[str] = mapped_column("org_id", VARCHAR(128))
    org_type: Mapped[str] = mapped_column("org_type", VARCHAR(128))
    origin: Mapped[str] = mapped_column("origin", VARCHAR(128))
    description: Mapped[str] = mapped_column("description", VARCHAR(1024))
    short_description: Mapped[str] = mapped_column("short_description", VARCHAR(1024))
    url: Mapped[str] = mapped_column("url", VARCHAR(512))
    duns_no: Mapped[str] = mapped_column("duns_no", VARCHAR(36))
    contacts: Mapped[dict] = mapped_column("contacts", JSON, nullable=False)
    assets: Mapped[dict] = mapped_column("assets", JSON, nullable=False)
    metadata_uri: Mapped[str] = mapped_column("metadata_uri", VARCHAR(255))
    groups: Mapped[dict] = mapped_column("groups", JSON, nullable=False)
    org_state: Mapped[dict] = mapped_column("org_state", JSON, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Service(Base):
    __tablename__ = "service"

    org_uuid: Mapped[str] = mapped_column(
        "org_uuid",
        VARCHAR(128),
        ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    uuid: Mapped[str] = mapped_column("uuid", VARCHAR(128), primary_key=True, nullable=False)
    display_name: Mapped[str] = mapped_column("display_name", VARCHAR(128), nullable=False)
    service_id: Mapped[str] = mapped_column("service_id", VARCHAR(128))
    metadata_uri: Mapped[str] = mapped_column("metadata_uri", VARCHAR(255))
    storage_provider: Mapped[str] = mapped_column("storage_provider", VARCHAR(128))
    proto: Mapped[dict] = mapped_column("proto", JSON, nullable=False, default={})
    short_description: Mapped[str] = mapped_column("short_description", VARCHAR(1024), nullable=False, default="")
    description: Mapped[str] = mapped_column("description", VARCHAR(1024), nullable=False, default="")
    project_url: Mapped[str] = mapped_column("project_url", VARCHAR(512))
    assets: Mapped[dict] = mapped_column("assets", JSON, nullable=False, default={})
    rating: Mapped[dict] = mapped_column("ratings", JSON, nullable=False, default={})
    ranking: Mapped[int] = mapped_column("ranking", Integer, nullable=False, default=1)
    contributors: Mapped[dict] = mapped_column("contributors", JSON, nullable=False, default=[])
    tags: Mapped[dict] = mapped_column("tags", JSON, nullable=False, default=[])
    mpe_address: Mapped[str] = mapped_column("mpe_address", VARCHAR(128), nullable=False, default="")
    service_type: Mapped[str] = mapped_column("service_type", VARCHAR(128))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    groups = relationship("ServiceGroup", uselist=True)
    service_state = relationship("ServiceState", uselist=False)
    offchain_service_config = relationship("OffchainServiceConfig", uselist=True)


class ServiceState(Base):
    __tablename__ = "service_state"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid: Mapped[str] = mapped_column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid: Mapped[str] = mapped_column(
        "service_uuid",
        VARCHAR(128),
        ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False
    )
    state: Mapped[str] = mapped_column("state", VARCHAR(128), nullable=False)
    transaction_hash: Mapped[str] = mapped_column("transaction_hash", VARCHAR(128))
    test_transaction_hash: Mapped[str] = mapped_column("test_transaction_hash", VARCHAR(128))
    created_by: Mapped[str] = mapped_column("created_by", VARCHAR(128), nullable=False)
    updated_by: Mapped[str] = mapped_column("updated_by", VARCHAR(128), nullable=False)
    approved_by: Mapped[str] = mapped_column("approved_by", VARCHAR(128))
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    UniqueConstraint(org_uuid, service_uuid, name="uq_org_srvc")


class ServiceGroup(Base):
    __tablename__ = "service_group"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid: Mapped[str] = mapped_column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid: Mapped[str] = mapped_column(
        "service_uuid",
        VARCHAR(128),
        ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    group_id: Mapped[str] = mapped_column("group_id", VARCHAR(128), nullable=False)
    group_name: Mapped[str] = mapped_column("group_name", VARCHAR(128), nullable=False, default="")
    pricing: Mapped[dict] = mapped_column("pricing", JSON, nullable=False, default=[])
    endpoints: Mapped[dict] = mapped_column("endpoints", JSON, nullable=False, default=[])
    test_endpoints: Mapped[dict] = mapped_column("test_endpoints", JSON, nullable=False, default=[])
    daemon_address: Mapped[dict] = mapped_column("daemon_address", JSON, nullable=False, default=[])
    free_calls: Mapped[int] = mapped_column("free_calls", Integer, nullable=False, default=0)
    free_call_signer_address: Mapped[str] = mapped_column("free_call_signer_address", VARCHAR(128))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    UniqueConstraint(org_uuid, service_uuid, group_id, name="uq_org_srvc_grp")


class ServiceReviewHistory(Base):
    __tablename__ = "service_review_history"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid: Mapped[str] = mapped_column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid: Mapped[str] = mapped_column("service_uuid", VARCHAR(128), nullable=False)
    service_metadata: Mapped[dict] = mapped_column("service_metadata", JSON, nullable=False)
    state: Mapped[str] = mapped_column("state", VARCHAR(64), nullable=False)
    reviewed_by: Mapped[str] = mapped_column("reviewed_by", VARCHAR(128))
    reviewed_on: Mapped[str] = mapped_column("reviewed_on", TIMESTAMP(timezone=False))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class ServiceComment(Base):
    __tablename__ = "service_comment"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid: Mapped[str] = mapped_column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid: Mapped[str] = mapped_column("service_uuid", VARCHAR(128), nullable=False)
    support_type: Mapped[str] = mapped_column("support_type", VARCHAR(128), nullable=False)
    user_type: Mapped[str] = mapped_column("user_type", VARCHAR(128), nullable=False)
    commented_by: Mapped[str] = mapped_column("commented_by", VARCHAR(128), nullable=False)
    comment = mapped_column("comment", TEXT, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class OffchainServiceConfig(Base):
    __tablename__ = "offchain_service_config"

    row_id: Mapped[int] = mapped_column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid: Mapped[str] = mapped_column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid: Mapped[str] = mapped_column(
        "service_uuid",
        VARCHAR(128),
        ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    parameter_name: Mapped[str] = mapped_column("parameter_name", VARCHAR(128), nullable=False)
    parameter_value: Mapped[str] = mapped_column("parameter_value", VARCHAR(512), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    UniqueConstraint(org_uuid, service_uuid, parameter_name, name="uq_off")