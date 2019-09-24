from sqlalchemy import Column, String, TIMESTAMP, UniqueConstraint, ForeignKeyConstraint, Index, JSON
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Service(Base):
    __tablename__ = 'service'

    row_id = Column(INTEGER, primary_key=True,
                    autoincrement=True, nullable=False)
    org_id = Column(INTEGER)
    service_id = Column(String)
    service_path = Column(String)
    ipfs_hash = Column(String)
    is_curated = Column(INTEGER)
    service_email = Column(String)
    row_created = Column(TIMESTAMP)
    row_updated = Column(TIMESTAMP)

    UniqueConstraint('org_id', 'service_id', name='uq_srvc')

    def __repr__(self):
        return "<User(row_id='%s', org_id='%s', service_id='%s')>" % (self.row_id, self.org_id, self.service_id)


class ServiceMetadata (Base):
    __tablename__ = 'service_metadata'

    row_id = Column(INTEGER, primary_key=True,
                    nullable=False, autoincrement=True)
    service_row_id = Column(INTEGER)
    org_id = Column(String)
    service_id = Column(String)
    display_name = Column(String)
    description = Column(String)
    url = Column(String)
    json = Column(String)
    model_ipfs_hash = Column(String)
    encoding = Column(String)
    type = Column(String)
    mpe_address = Column(String)
    assets_url = Column(JSON)
    assets_hash = Column(JSON)
    service_rating = Column(JSON)
    contributors = Column(String)
    ranking = Column(INTEGER)
    row_created = Column(TIMESTAMP)
    row_updated = Column(TIMESTAMP)

    UniqueConstraint('org_id', 'service_id', name='uq_srvc_mdata')
    ForeignKeyConstraint(
        ['service_row_id'], ['service.row_id'],
        name='ServiceMdataFK', ondelete=True
    )
    Index('ServiceFK_idx', 'service_row_id')

    def __repr__(self):
        return "<User(row_id='%s', org_id='%s', service_id='%s')>" % (self.row_id, self.org_id, self.service_id)
