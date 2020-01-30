from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organization"
    row_id = Column("row_id", Integer, autoincrement=True)
    uuid = Column("uuid", VARCHAR(128), primary_key=True)
    name = Column("name", VARCHAR(128))
    org_id = Column("org_id", VARCHAR(128))
    type = Column("type", VARCHAR(128))
    origin = Column("origin", VARCHAR(128))
    description = Column("description", VARCHAR(1024))
    short_description = Column("short_description", VARCHAR(1024))
    url = Column("url", VARCHAR(512))
    duns_no = Column("duns_no", VARCHAR(36))
    contacts = Column("contacts", JSON, nullable=False)
    assets = Column("assets", JSON, nullable=False)
    metadata_ipfs_hash = Column("metadata_ipfs_hash", VARCHAR(255))
    org_status = relationship("Group", backref='organization', lazy='joined')
    groups = relationship("Group", backref='organization', lazy='joined')
    address = relationship("OrganizationAddress", backref='organization', lazy='joined')


class OrganizationAddress(Base):
    __tablename__ = "organization_address"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", Integer,
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"),
                      nullable=False)
    address_type = Column("address_type", VARCHAR(64), nullable=False)
    street_address = Column("street_address", VARCHAR(256), nullable=False)
    apartment = Column("apartment", VARCHAR(256), nullable=False)
    city = Column("city", VARCHAR(64), nullable=False)
    pincode = Column("pincode", Integer, nullable=False)
    state = Column("state", VARCHAR(64), nullable=True)
    country = Column("country", VARCHAR(64), nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))


class OrganizationStatus:
    __tablename__ = "orgazanition_status"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", Integer,
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column("status", VARCHAR(128), nullable=False)
    transaction_hash = Column("transaction_hash", VARCHAR(128))
    wallet_address = Column("user_address", VARCHAR(128))
    created_by = Column("created_by", VARCHAR(128), nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_by = Column("updated_by", VARCHAR(128), nullable=False)
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    approved_by = Column("approved_by", VARCHAR(128))
    approved_on = Column("approved_on", TIMESTAMP(timezone=False))


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
    row_id = Column("row_id", Integer, autoincrement=True)
    name = Column("name", VARCHAR(128), nullable=False)
    id = Column("id", VARCHAR(128), nullable=False)
    org_uuid = Column("org_uuid", VARCHAR(128),
                      ForeignKey("organization.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    payment_address = Column("payment_address", VARCHAR(128), nullable=False)
    payment_config = Column("payment_config", JSON, nullable=False)
    status = Column("status", VARCHAR(128))
