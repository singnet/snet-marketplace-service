from datetime import datetime

from sqlalchemy import Column, VARCHAR, Integer, ForeignKey, UniqueConstraint, null, DECIMAL, BIGINT, Index, TEXT
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP, TINYINT, BIT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DaemonToken(Base):
    __tablename__ = "daemon_token"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    daemon_id = Column("daemon_id", VARCHAR(256), nullable=False)
    token = Column("token", VARCHAR(128), nullable=False)
    expiration = Column("expiration", VARCHAR(256), nullable=False)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(daemon_id, name="uq_daemon_id")
    Index("daemon_id_idx", daemon_id)


class Members(Base):
    __tablename__ = "members"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    org_id = Column("org_id", VARCHAR(128),
                    ForeignKey("organization.org_id", ondelete="CASCADE"),
                    nullable=False)
    member = Column("member", VARCHAR(128), nullable=False)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    Index("MembersFK_idx", org_id)


class MpeChannel(Base):
    __tablename__ = "mpe_channel"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    channel_id = Column("channel_id", Integer, nullable=False)
    sender = Column("sender", VARCHAR(128), nullable=False)
    recipient = Column("recipient", VARCHAR(128), nullable=False)
    groupId = Column("groupId", VARCHAR(128), nullable=False)
    balance_in_cogs = Column("balance_in_cogs", DECIMAL(19, 8), default=null)
    pending = Column("pending", DECIMAL(19, 8), default=null)
    nonce = Column("nonce", Integer, default=null)
    expiration = Column("expiration", BIGINT, default=null)
    signer = Column("signer", VARCHAR(256), nullable=False)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    consumed_balance = Column("consumed_balance", DECIMAL(10, 0), default=0)
    UniqueConstraint(channel_id, sender, recipient, groupId, name="uq_channel")


class OrgGroup(Base):
    __tablename__ = "org_group"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    group_id = Column("group_id", VARCHAR(256), default=null)
    group_name = Column("group_name", VARCHAR(128), default=null)
    payment = Column("payment", JSON, default=null)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(org_id, group_id, name="uq_org_grp")


class Organization(Base):
    __tablename__ = "organization"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    organization_name = Column("organization_name", VARCHAR(128), default=null)
    owner_address = Column("owner_address", VARCHAR(256), default=null)
    org_metadata_uri = Column("org_metadata_uri", VARCHAR(128), default=null)
    org_email = Column("org_email", VARCHAR(128), default=null)
    org_assets_url = Column("org_assets_url", JSON, default=null)
    is_curated = Column("is_curated", TINYINT, default=null)
    description = Column("description", VARCHAR(256), default=null)
    assets_hash = Column("assets_hash", JSON, default=null)
    contacts = Column("contacts", JSON, default=null)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(org_id, name="uq_org")


class Service(Base):
    __tablename__ = "service"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128), nullable=False)
    service_path = Column("service_path", VARCHAR(128), default=null)
    ipfs_hash = Column("ipfs_hash", VARCHAR(128), default=null)
    is_curated = Column("is_curated", TINYINT, default=null)
    service_email = Column("service_email", VARCHAR(128), default=null)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    service_metadata = relationship("ServiceMetadata", uselist=False)
    UniqueConstraint(org_id, service_id, name="uq_srvc")


class ServiceEndpoint(Base):
    __tablename__ = "service_endpoint"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id = Column("service_row_id", Integer,
                            ForeignKey("service.row_id", ondelete="CASCADE"),
                            nullable=False)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128), nullable=False)
    group_id = Column("group_id", VARCHAR(256), nullable=False)
    endpoint = Column("endpoint", VARCHAR(256), default=null)
    is_available = Column("is_available", BIT(1), default=null)
    last_check_timestamp = Column("last_check_timestamp", TIMESTAMP(timezone=False), nullable=True, default=null)
    next_check_timestamp = Column("next_check_timestamp", TIMESTAMP(timezone=False), nullable=True,
                                  default=datetime.utcnow())
    failed_status_count = Column("failed_status_count", Integer, default=1)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    Index("ServiceFK_idx", service_row_id)


class ServiceGroup(Base):
    __tablename__ = "service_group"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id = Column("service_row_id", Integer,
                            ForeignKey("service.row_id", ondelete="CASCADE"),
                            nullable=False)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128), nullable=False)
    free_call_signer_address = Column("free_call_signer_address", VARCHAR(256), default=null)
    free_calls = Column("free_calls", Integer, default=null)
    group_id = Column("group_id", VARCHAR(256), nullable=False)
    group_name = Column("group_name", VARCHAR(128), nullable=False)
    pricing = Column("pricing", JSON, default=null)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    Index("ServiceFK_idx", service_row_id)
    UniqueConstraint(org_id, service_id, group_id, name="uq_srvc_grp")


class ServiceMedia(Base):
    __tablename__ = "service_media"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id = Column("org_id", VARCHAR(100), nullable=False)
    service_id = Column("service_id", VARCHAR(100), nullable=False)
    url = Column("url", VARCHAR(512), default=null)
    order = Column("order", Integer, default=null)
    file_type = Column("file_type", VARCHAR(100), default=null)
    asset_type = Column("asset_type", VARCHAR(100), default=null)
    alt_text = Column("alt_text", VARCHAR(100), default=null)
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=True, default=null)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=True, default=null)
    ipfs_url = Column("ipfs_url", VARCHAR(512), default=null)
    service_row_id = Column("service_row_id", Integer,
                            ForeignKey("service.row_id", ondelete="CASCADE"),
                            default=null)
    Index("ServiceMedisFK", service_row_id)


class ServiceMetadata(Base):
    __tablename__ = "service_metadata"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id = Column("service_row_id", Integer,
                            ForeignKey("service.row_id", ondelete="CASCADE"),
                            nullable=False)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128), nullable=False)
    display_name = Column("display_name", VARCHAR(256), default=null)
    description = Column("description", VARCHAR(1024), default=null)
    short_description = Column("short_description", VARCHAR(1024), default=null)
    demo_component_available = Column("demo_component_available", TINYINT(1), default=0, server_default="0", nullable=False)
    url = Column("url", VARCHAR(256), default=null)
    json = Column("json", VARCHAR(1024), default=null)
    model_ipfs_hash = Column("model_ipfs_hash", VARCHAR(256), default=null)
    encoding = Column("encoding", VARCHAR(128), default=null)
    type = Column("type", VARCHAR(128), default=null)
    mpe_address = Column("mpe_address", VARCHAR(256), default=null)
    assets_url = Column("assets_url", JSON, default=null)
    assets_hash = Column("assets_hash", JSON, default=null)
    service_rating = Column("service_rating", JSON, default=null)
    ranking = Column("ranking", Integer, default=1)
    contributors = Column("contributors", JSON, default=null)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(org_id, service_id, name="uq_srvc_mdata")
    Index("ServiceFK_idx", service_row_id)


class ServiceTags(Base):
    __tablename__ = "service_tags"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    service_row_id = Column("service_row_id", Integer,
                            ForeignKey("service.row_id", ondelete="CASCADE"),
                            nullable=False)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128), default=null)
    tag_name = Column("tag_name", VARCHAR(128), default=null)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    UniqueConstraint(org_id, service_id, tag_name, name="uq_srvc_tag")
    Index("ServiceFK_idx", service_row_id)


class Banner(Base):
    __tablename__ = "banner"
    id = Column("id", Integer, primary_key=True)
    image = Column("image", VARCHAR(256))
    image_alignment = Column("image_alignment", VARCHAR(128))
    alt_text = Column("alt_text", VARCHAR(256))
    title = Column("title", VARCHAR(256))
    rank = Column("rank", Integer)
    description = Column("description", TEXT)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    cta_order_rank = relationship("CTA", backref="banner", lazy="joined", order_by="CTA.rank")


class CTA(Base):
    __tablename__ = "cta"
    id = Column("id", Integer, primary_key=True)
    banner_id = Column("banner_id", Integer, ForeignKey("banner.id", ondelete="CASCADE", onupdate="CASCADE"))
    text = Column("text", VARCHAR(256))
    url = Column("url", VARCHAR(256))
    type = Column("type", VARCHAR(256))
    variant = Column("variant", VARCHAR(256))
    rank = Column("rank", Integer)
    row_created = Column("row_created", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())
    row_updated = Column("row_updated", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())

class OffchainServiceConfig(Base):
    __tablename__ = "offchain_service_config"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128), nullable=False)
    demo_component_required = Column("demo_component_required", TINYINT(1), default=0, server_default="0",
                                         nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow())