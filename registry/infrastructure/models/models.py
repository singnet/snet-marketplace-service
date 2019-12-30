from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organization"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", VARCHAR(128), nullable=False)
    org_uuid = Column("org_uuid", VARCHAR(128))
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    type = Column("type", VARCHAR(128), nullable=False)
    description = Column("description", VARCHAR(1024), nullable=False)
    short_description = Column("short_description", VARCHAR(1024), nullable=False)
    url = Column("url", VARCHAR(512), nullable=False)
    duns_no = Column("duns_no", VARCHAR(20), nullable=True)
    contacts = Column("contacts", JSON, nullable=False)
    assets = Column("assets", JSON, nullable=False)
    metadata_ipfs_hash = Column("metadata_ipfs_hash", VARCHAR(255))
    groups = relationship("Group", backref='organization', lazy='joined')
    address = relationship("OrganizationAddress", uselist=False, back_populates="organization")


class OrganizationReviewWorkflow(Base):
    __tablename__ = "organization_review_workflow"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_row_id = Column("organization_row_id", Integer, nullable=False)
    status = Column("status", VARCHAR(128), nullable=False)
    created_by = Column("created_by", VARCHAR(128), nullable=False)
    updated_by = Column("updated_by", VARCHAR(128), nullable=False)
    approved_by = Column("approved_by", VARCHAR(128))
    create_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("modified_on", TIMESTAMP(timezone=False))


class OrganizationAddress(Base):
    __tablename__ = "organization_address"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_row_id = Column("org_row_id", Integer,
                        ForeignKey("organization.row_id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)
    headquater_address = Column("headquater_address", JSON, nullable=False)
    mailing_address = Column("mailing_address", JSON, nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    organization = relationship("Organization", back_populates="address")


class OrganizationAddressHistory(Base):
    __tablename__ = "organization_address_history"
    row_id = Column("row_id", Integer, primary_key=True)
    org_row_id = Column("org_row_id", Integer,
                        ForeignKey("organization_history.row_id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)
    headquater_address = Column("headquater_address", JSON, nullable=False)
    mailing_address = Column("mailing_address", JSON, nullable=False)
    created_on = Column("created_on", TIMESTAMP(timezone=False))
    updated_on = Column("updated_on", TIMESTAMP(timezone=False))
    organization = relationship("OrganizationHistory", back_populates="address")


class OrganizationHistory(Base):
    __tablename__ = "organization_history"
    row_id = Column("row_id", Integer, primary_key=True)
    name = Column("name", VARCHAR(128), nullable=False)
    org_uuid = Column("org_uuid", VARCHAR(128))
    org_id = Column("org_id", VARCHAR(128), nullable=False)
    type = Column("type", VARCHAR(128), nullable=False)
    description = Column("description", VARCHAR(1024), nullable=False)
    short_description = Column("short_description", VARCHAR(1024), nullable=False)
    url = Column("url", VARCHAR(512), nullable=False)
    contacts = Column("contacts", JSON, nullable=False)
    assets = Column("assets", JSON, nullable=False)
    metadata_ipfs_hash = Column("metadata_ipfs_hash", VARCHAR(255))
    groups = relationship('GroupHistory', backref='organization_history', lazy='joined')
    address = relationship("OrganizationAddressHistory", uselist=False, back_populates="organization")


class Group(Base):
    __tablename__ = "group"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", VARCHAR(128), nullable=False)
    id = Column("id", VARCHAR(128), nullable=False)
    org_uuid = Column("org_uuid", VARCHAR(128))
    org_row_id = Column("org_row_id", Integer,
                        ForeignKey("organization.row_id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)
    payment_address = Column("payment_address", VARCHAR(128), nullable=False)
    payment_config = Column("payment_config", JSON, nullable=False)
    status = Column("status", VARCHAR(128))


class GroupHistory(Base):
    __tablename__ = "group_history"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", VARCHAR(128), nullable=False)
    id = Column("id", VARCHAR(128), nullable=False)
    org_uuid = Column("org_uuid", VARCHAR(128))
    org_row_id = Column("org_row_id", Integer,
                        ForeignKey("organization_history.row_id", ondelete="CASCADE", onupdate="CASCADE"),
                        nullable=False)
    payment_address = Column("payment_address", VARCHAR(128), nullable=False)
    payment_config = Column("payment_config", JSON, nullable=False)
    status = Column("status", VARCHAR(128))


class OrganizationMember(Base):
    __tablename__ = "org_member"
    row_id = Column("row_id", Integer, primary_key=True, autoincrement=True)
    org_uuid = Column("org_uuid", VARCHAR(128))
    role = Column("role", VARCHAR(128))
    username = Column("username", VARCHAR(128))
