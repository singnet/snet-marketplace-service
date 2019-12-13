from sqlalchemy import Column, Integer, VARCHAR
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from registry.infrastructure.models import Base


class Organization(Base):
    __tablename__ = "organization"
    row_id = Column("row_id", Integer, primary_key=True)
    name = Column("name", VARCHAR(128), nullable=False)
    id = Column("id", VARCHAR(128), nullable=False, unique=True)
    type = Column("type", VARCHAR(128), nullable=False)
    description = Column("description", VARCHAR(1024), nullable=False)
    short_description = Column("short_description", VARCHAR(1024), nullable=False)
    url = Column("url", VARCHAR(512), nullable=False)
    contacts = Column("contacts", JSON, nullable=False)
    assets = Column("assets", JSON, nullable=False)
    groups = relationship('Group', backref='organization', lazy='joined')


class WorkFlow(Base):
    __tablename__ = "organization_review_workflow"
    row_id = Column("row_id", Integer, primary_key=True)
    org_row_id = Column("organization_row_id", Integer, nullable=False)
    status = Column("status", VARCHAR(128), nullable=False)
    created_by = Column("created_by", VARCHAR(128), nullable=False)
    updated_by = Column("updated_by", VARCHAR(128), nullable=False)
    approved_by = Column("approved_by", VARCHAR(128))


class OrganizationArchive(Base):
    __tablename__ = "organization_archive"
    row_id = Column("row_id", Integer, primary_key=True)
    name = Column("name", VARCHAR(128), nullable=False)
    id = Column("id", VARCHAR(128), nullable=False, unique=True)
    type = Column("type", VARCHAR(128), nullable=False)
    description = Column("description", VARCHAR(1024), nullable=False)
    short_description = Column("short_description", VARCHAR(1024), nullable=False)
    url = Column("url", VARCHAR(512), nullable=False)
    contacts = Column("contacts", JSON, nullable=False)
    assets = Column("assets", JSON, nullable=False)
    groups = relationship('Group', backref='organization', lazy='joined')
