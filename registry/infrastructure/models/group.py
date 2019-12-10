from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from registry.infrastructure.models import Base


class Group(Base):
    __tablename__ = "groups"
    row_id = Column("row_id", Integer, primary_key=True)
    name = Column("name", VARCHAR(128), nullable=False)
    id = Column("id", VARCHAR(128), nullable=False)
    org_id = Column("org_id", VARCHAR(128),
                    ForeignKey("order.id", ondelete="CASCADE", onupdate="CASCADE"))
    payment_address = Column("payment_address", VARCHAR(128), nullable=False)
    payment_config = Column("payment_config", JSON, nullable=False)
