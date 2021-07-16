from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP, VARCHAR, TEXT, TINYINT
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
    metadata_ipfs_uri = Column("metadata_ipfs_uri", VARCHAR(255))
    org_state = relationship("OrganizationState", backref='organization', lazy='joined')
    groups = relationship("Group", backref='organization', lazy='joined')
    addresses = relationship("OrganizationAddress", backref='organization', lazy='joined')


class OrganizationAddress(Base):
    __tablename__ = "organization_address"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                      nullable=False)
    address_type = Column("address_type", VARCHAR(64))
    street_address = Column("street_address", VARCHAR(256))
    apartment = Column("apartment", VARCHAR(256))
    city = Column("city", VARCHAR(64))
    pincode = Column("pincode", VARCHAR(64))
    state = Column("state", VARCHAR(64))
    country = Column("country", VARCHAR(64))
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))


class OrganizationState(Base):
    __tablename__ = "organization_state"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    state = Column("state", VARCHAR(128), nullable=False)
    transaction_hash = Column("transaction_hash", VARCHAR(128))
    nonce = Column("nonce", Integer)
    test_transaction_hash = Column("test_transaction_hash", VARCHAR(128))
    wallet_address = Column("user_address", VARCHAR(128))
    created_by = Column("created_by", VARCHAR(128), nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_by = Column("updated_by", VARCHAR(128), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    reviewed_by = Column("approved_by", VARCHAR(128))
    reviewed_on = Column("approved_on", TIMESTAMP(timezone=False))
    comments = Column("comments", JSON, default=[])


class OrganizationMember(Base):
    __tablename__ = "org_member"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    invite_code = Column("invite_code", VARCHAR(128))
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
    payment_address = Column("payment_address", VARCHAR(128))
    payment_config = Column("payment_config", JSON, nullable=False)
    status = Column("status", VARCHAR(128))


class OrganizationArchive(Base):
    __tablename__ = "organization_archive"
    row_id = Column("row_id", Integer, autoincrement=True, primary_key=True)
    uuid = Column("uuid", VARCHAR(128))
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
    metadata_ipfs_uri = Column("metadata_ipfs_uri", VARCHAR(255))
    groups = Column("groups", JSON, nullable=False)
    org_state = Column("org_state", JSON, nullable=False)


class Service(Base):
    __tablename__ = "service"
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                      nullable=False)
    uuid = Column("uuid", VARCHAR(128), primary_key=True, nullable=False)
    display_name = Column("display_name", VARCHAR(128), nullable=False)
    service_id = Column("service_id", VARCHAR(128))
    metadata_uri = Column("metadata_uri", VARCHAR(255))
    proto = Column("proto", JSON, nullable=False, default={})
    short_description = Column("short_description", VARCHAR(1024), nullable=False, default="")
    description = Column("description", VARCHAR(1024), nullable=False, default="")
    project_url = Column("project_url", VARCHAR(512))
    assets = Column("assets", JSON, nullable=False, default={})
    rating = Column("ratings", JSON, nullable=False, default={})
    ranking = Column("ranking", Integer, nullable=False, default=1)
    contributors = Column("contributors", JSON, nullable=False, default=[])
    tags = Column("tags", JSON, nullable=False, default=[])
    mpe_address = Column("mpe_address", VARCHAR(128), nullable=False, default="")
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow())
    groups = relationship("ServiceGroup", uselist=True)
    service_state = relationship("ServiceState", uselist=False)


class ServiceState(Base):
    __tablename__ = "service_state"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128),
                          ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                          unique=True, nullable=False)
    state = Column("state", VARCHAR(128), nullable=False)
    transaction_hash = Column("transaction_hash", VARCHAR(128))
    test_transaction_hash = Column("test_transaction_hash", VARCHAR(128))
    created_by = Column("created_by", VARCHAR(128), nullable=False)
    updated_by = Column("updated_by", VARCHAR(128), nullable=False)
    approved_by = Column("approved_by", VARCHAR(128))
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow())
    UniqueConstraint(org_uuid, service_uuid, name="uq_org_srvc")


class ServiceGroup(Base):
    __tablename__ = "service_group"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128),
                          ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=False)
    group_id = Column("group_id", VARCHAR(128), nullable=False)
    group_name = Column("group_name", VARCHAR(128), nullable=False, default="")
    pricing = Column("pricing", JSON, nullable=False, default=[])
    endpoints = Column("endpoints", JSON, nullable=False, default=[])
    test_endpoints = Column("test_endpoints", JSON, nullable=False, default=[])
    daemon_address = Column("daemon_address", JSON, nullable=False, default=[])
    free_calls = Column("free_calls", Integer, nullable=False, default=0)
    free_call_signer_address = Column("free_call_signer_address", VARCHAR(128))
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow())
    UniqueConstraint(org_uuid, service_uuid, group_id, name="uq_org_srvc_grp")


class ServiceReviewHistory(Base):
    __tablename__ = "service_review_history"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128), nullable=False)
    service_metadata = Column("service_metadata", JSON, nullable=False)
    state = Column("state", VARCHAR(64), nullable=False)
    reviewed_by = Column("reviewed_by", VARCHAR(128))
    reviewed_on = Column("reviewed_on", TIMESTAMP(timezone=False))
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow())


class ServiceComment(Base):
    __tablename__ = "service_comment"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128), nullable=False)
    support_type = Column("support_type", VARCHAR(128), nullable=False)
    user_type = Column("user_type", VARCHAR(128), nullable=False)
    commented_by = Column("commented_by", VARCHAR(128), nullable=False)
    comment = Column("comment", TEXT, nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow())


class OffchainServiceConfig(Base):
    __tablename__ = "offchain_service_config"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128), nullable=False)
    service_uuid = Column("service_uuid", VARCHAR(128),
                          ForeignKey("service.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=False)
    demo_component_required = Column("demo_component_required", TINYINT(1), default=0, server_default="0",
                                     nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False), nullable=False, default=datetime.utcnow())
