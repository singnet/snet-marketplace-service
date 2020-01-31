from sqlalchemy import Column, ForeignKey, Integer, VARCHAR, UniqueConstraint, BOOLEAN, PrimaryKeyConstraint
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organization"
    uuid = Column("uuid", VARCHAR(128), primary_key=True)
    name = Column("name", VARCHAR(128))
    org_id = Column("org_id", VARCHAR(128))
    org_type = Column("org_type", VARCHAR(128))
    origin = Column("origin", VARCHAR(128))
    description = Column("description", VARCHAR(1024))
    short_description = Column("short_description", VARCHAR(1024))
    url = Column("url", VARCHAR(512))
    duns_no = Column("duns_no", VARCHAR(36))
    contacts = Column("contacts", JSON, nullable=False)
    assets = Column("assets", JSON, nullable=False)
    metadata_ipfs_hash = Column("metadata_ipfs_hash", VARCHAR(255))
    org_state = relationship("OrganizationState", backref='organization', lazy='joined')
    groups = relationship("Group", backref='organization', lazy='joined')
    addresses = relationship("OrganizationAddress", backref='organization', lazy='joined')


class OrganizationAddress(Base):
    __tablename__ = "organization_address"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                      nullable=False)
    address_type = Column("address_type", VARCHAR(64), nullable=False)
    street_address = Column("street_address", VARCHAR(256), nullable=False)
    apartment = Column("apartment", VARCHAR(256), nullable=False)
    city = Column("city", VARCHAR(64), nullable=False)
    pincode = Column("pincode", VARCHAR(64), nullable=False)
    state = Column("state", VARCHAR(64), nullable=True)
    country = Column("country", VARCHAR(64), nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))


class OrganizationState(Base):
    __tablename__ = "organization_state"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    state = Column("state", VARCHAR(128), nullable=False)
    transaction_hash = Column("transaction_hash", VARCHAR(128))
    wallet_address = Column("user_address", VARCHAR(128))
    created_by = Column("created_by", VARCHAR(128), nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_by = Column("updated_by", VARCHAR(128), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    reviewed_by = Column("approved_by", VARCHAR(128))
    reviewed_on = Column("approved_on", TIMESTAMP(timezone=False))


class OrganizationMember(Base):
    __tablename__ = "org_member"
    row_id = Column("row_id", Integer, autoincrement=True)
    invite_code = Column("invite_code", VARCHAR(128), primary_key=True)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    role = Column("role", VARCHAR(128))
    username = Column("username", VARCHAR(128))
    address = Column("address", VARCHAR(128))
    status = Column("status", VARCHAR(128))
    transaction_hash = Column("transaction_hash", VARCHAR(128))
    invited_on = Column("invited_on", TIMESTAMP(timezone=False))
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))


class Group(Base):
    __tablename__ = "group"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    name = Column("name", VARCHAR(128), nullable=False)
    id = Column("id", VARCHAR(128), nullable=False)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    payment_address = Column("payment_address", VARCHAR(128), nullable=False)
    payment_config = Column("payment_config", JSON, nullable=False)
    status = Column("status", VARCHAR(128))


class Service(Base):
    __tablename__ = "service"
    row_id = Column("row_id", Integer, unique=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                      nullable=False)
    uuid = Column("uuid", VARCHAR(128), primary_key=True, nullable=False)
    display_name = Column("display_name", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128), nullable=False)
    metadata_ipfs_hash = Column("metadata_ipfs_hash", VARCHAR(255))
    proto = Column("proto", JSON, nullable=False)
    short_description = Column("short_description", VARCHAR(1024), nullable=False)
    description = Column("description", VARCHAR(1024), nullable=False)
    project_url = Column("git_url", VARCHAR(512), nullable=False)
    assets = Column("assets", JSON, nullable=False)
    rating = Column("ratings", JSON, nullable=False)
    ranking = Column("ranking", Integer, nullable=False, default=1)
    contributors = Column("contributors", JSON, nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))


class ServiceReviewWorkflow(Base):
    __tablename__ = "service_review_workflow"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128),
                          ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                          unique=True, nullable=False)
    state = Column("state", VARCHAR(128), nullable=False)
    transaction_hash = Column("transaction_hash", VARCHAR(128))
    created_by = Column("created_by", VARCHAR(128), nullable=False)
    updated_by = Column("updated_by", VARCHAR(128), nullable=False)
    approved_by = Column("approved_by", VARCHAR(128))
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    UniqueConstraint(org_uuid, service_uuid, name="uq_org_srvc")


class ServiceGroup(Base):
    __tablename__ = "service_group"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128),
                          ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=False)
    group_id = Column("group_id", VARCHAR(128), unique=True, nullable=False)
    pricing = Column("pricing", JSON, nullable=False)
    endpoints = Column("endpoints", JSON, nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    UniqueConstraint(org_uuid, service_uuid, group_id, name="uq_org_srvc_grp")


class ServiceReviewHistory(Base):
    __tablename__ = "service_review_history"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128), nullable=False)
    reviewed_service_data = Column("reviewed_service_data", JSON, nullable=False)
    state = Column("state", VARCHAR(64), nullable=False)
    reviewed_by = Column("reviewed_by", VARCHAR(128), nullable=False)
    reviewed_on = Column("reviewed_on", TIMESTAMP(timezone=False))
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))

# do not delete below commented schema
# class ServiceEndpoint(Base):
#     __tablename__ = "service_endpoint"
#     row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
#     service_group_row_id = Column("service_group_row_id", Integer,
#                                   ForeignKey("service_group.row_id", ondelete="CASCADE", onupdate="CASCADE"),
#                                   nullable=False)
#     endpoint = Column("endpoint", VARCHAR(256), nullable=False)
#     is_available = Column("is_available", BOOLEAN, nullable=False)
#     last_check_timestamp = Column("last_check_timestamp", TIMESTAMP(timezone=False))
#     next_check_timestamp = Column("next_check_timestamp", TIMESTAMP(timezone=False))
#     failed_status_count = Column("failed_status_count", Integer, default=1)
#     created_on = Column("created_on", TIMESTAMP(timezone=False))
#     updated_on = Column("updated_on", TIMESTAMP(timezone=False))
