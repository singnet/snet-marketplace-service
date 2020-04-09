from sqlalchemy import Column, Integer, VARCHAR, JSON, TIMESTAMP
from sqlalchemy.dialects.mysql import BIT, TINYINT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organization"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    org_id = Column("org_id", VARCHAR(128))
    organization_name = Column("organization_name", VARCHAR(128))
    owner_address = Column("owner_address", VARCHAR(256))
    org_metadata_uri = Column("org_metadata_uri", VARCHAR(128))
    org_email = Column("org_email", VARCHAR(128))
    org_assets_url = Column("org_assets_url", JSON)
    row_created = Column("row_created", TIMESTAMP(timezone=False))
    row_updated = Column("row_updated", TIMESTAMP(timezone=False))
    description = Column("description", JSON)
    assets_hash = Column("assets_hash", JSON)
    contacts = Column("contacts", JSON)


class Group(Base):
    __tablename__ = "org_group"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    org_id = Column("org_id", VARCHAR(128))
    group_id = Column("group_id", VARCHAR(128))
    group_name = Column("group_name", VARCHAR(128))
    payment = Column("payment", JSON)
    row_created = Column("row_created", TIMESTAMP(timezone=True))
    row_updated = Column("row_updated", TIMESTAMP(timezone=True))


class Service(Base):
    __tablename__ = "service"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    service_id = Column("service_id", VARCHAR(128))
    org_id = Column("org_id", VARCHAR(128))
    service_path = Column("service_path", VARCHAR(128))
    ipfs_hash = Column("ipfs_hash", VARCHAR(128))
    is_curated = Column("is_curated", TINYINT)
    service_email = Column("service_email", VARCHAR(128))
    row_created = Column("row_created", TIMESTAMP(timezone=False))
    row_updated = Column("row_updated", TIMESTAMP(timezone=False))


class ServiceMetadata(Base):
    __tablename__ = "service_metadata"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    service_row_id = Column("service_row_id", Integer)
    org_id = Column("org_id", VARCHAR(128))
    service_id = Column("service_id", VARCHAR(128))
    display_name = Column("display_name", VARCHAR(256))
    description = Column("description", VARCHAR(1024))
    short_description = Column("short_description", VARCHAR(256))
    url = Column("url", VARCHAR(256))
    json = Column("json", VARCHAR(1024))
    model_ipfs_hash = Column("model_ipfs_hash", VARCHAR(256))
    encoding = Column("encoding", VARCHAR(128))
    type = Column("type", VARCHAR(128))
    mpe_address = Column("mpe_address", VARCHAR(256))
    assets_url = Column("assets_url", JSON)
    assets_hash = Column("assets_hash", JSON)
    service_rating = Column("service_rating", JSON)
    ranking = Column("ranking", Integer)
    contributors = Column("contributors", JSON)
    row_created = Column("row_created", TIMESTAMP(timezone=False))
    row_updated = Column("row_updated", TIMESTAMP(timezone=False))


class ServiceGroup(Base):
    __tablename__ = "service_group"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    service_row_id = Column("service_row_id", Integer)
    org_id = Column("org_id", VARCHAR(128))
    service_id = Column("service_id", VARCHAR(128))
    group_id = Column("group_id", VARCHAR(256))
    group_name = Column("group_name", VARCHAR(128))
    pricing = Column("pricing", JSON)
    row_created = Column("row_created", TIMESTAMP(timezone=False))
    row_updated = Column("row_updated", TIMESTAMP(timezone=False))


class ServiceEndpoints(Base):
    __tablename__ = "service_endpoint"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    service_row_id = Column("service_row_id", Integer)
    org_id = Column("org_id", VARCHAR(128))
    service_id = Column("service_id", VARCHAR(128))
    group_id = Column("group_id", VARCHAR(256))
    endpoint = Column("endpoint", VARCHAR(256))
    is_available = Column("is_available", BIT)
    last_check_timestamp = Column("last_check_timestamp", TIMESTAMP(timezone=False))
    next_check_timestamp = Column("next_check_timestamp", TIMESTAMP(timezone=False))
    failed_status_count = Column("failed_status_count", TIMESTAMP(timezone=False))
    row_created = Column("row_created", TIMESTAMP(timezone=False))
    row_updated = Column("row_updated", TIMESTAMP(timezone=False))


class ServiceTags(Base):
    __tablename__ = "service_tags"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    service_row_id = Column("service_row_id", Integer)
    org_id = Column("org_id", VARCHAR(128))
    service_id = Column("service_id", VARCHAR(128))
    tag_name = Column("tag_name", VARCHAR(128))
    row_created = Column("row_created", TIMESTAMP(timezone=False))
    row_updated = Column("row_updated", TIMESTAMP(timezone=False))
