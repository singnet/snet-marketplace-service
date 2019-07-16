from sqlalchemy import Column, String, TIMESTAMP, UniqueConstraint, ForeignKeyConstraint, Index, JSON
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
class Service(Base):
    __tablename__ = 'service'

    row_id = Column(INTEGER, primary_key=True,autoincrement=True,nullable=False)
    org_id = Column(INTEGER)
    service_id = Column(String)
    service_path = Column(String)
    ipfs_hash = Column(String)
    is_curated= Column(INTEGER)
    row_created = Column(TIMESTAMP)
    row_updated= Column(TIMESTAMP)

    UniqueConstraint('org_id','service_id', name='uq_srvc')

    def __repr__(self):
        return "<User(row_id='%s', org_id='%s', service_id='%s')>" % (self.row_id, self.org_id, self.service_id)



class ServiceMetadata (Base):
    __tablename__ = 'service_metadata'

    row_id = Column(INTEGER, primary_key=True,nullable=False,autoincrement=True)
    service_row_id = Column(INTEGER)
    org_id = Column(String)
    #service_path = Column(String)
    service_id = Column(String)
    price_model= Column(INTEGER)
    price_in_cogs = Column(TIMESTAMP)
    display_name= Column(TIMESTAMP)
    description = Column(TIMESTAMP)
    url = Column(TIMESTAMP)
    json= Column(TIMESTAMP)
    model_ipfs_hash = Column(TIMESTAMP)
    encoding = Column(TIMESTAMP)
    type = Column(TIMESTAMP)
    mpe_address = Column(TIMESTAMP)

    payment_expiration_threshold = Column(TIMESTAMP)
    row_created = Column(TIMESTAMP)
    row_updated = Column(TIMESTAMP)
    assets_url =Column(JSON)
    assets_hash =Column(JSON)
    display_image_url= Column(String)



    UniqueConstraint('org_id','service_id',name='uq_srvc_mdata')
    ForeignKeyConstraint(
        ['service_row_id'], ['service.row_id'],
        name='ServiceMdataFK' ,ondelete=True
    )
    Index('ServiceFK_idx','service_row_id')


    def __repr__(self):
        return "<User(row_id='%s', org_id='%s', service_id='%s')>" % (self.row_id, self.org_id, self.service_id)

