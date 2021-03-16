from datetime import datetime

from sqlalchemy import Column, VARCHAR, Integer, ForeignKey, UniqueConstraint, null, DECIMAL, BIGINT, Index, TEXT
from sqlalchemy.dialects.mysql import JSON, TIMESTAMP, TINYINT, BIT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class HistoricalCryptoFiatExchangeRates(Base):
    __tablename__ = "historical_crypto_fiat_exhange_rates"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    crypto_symbol = Column("crypto_symbol", VARCHAR(100), nullable=False)
    fiat_symbol = Column("fiat_symbol", VARCHAR(100), nullable=False)
    crypto_rate = Column("crypto_rate", DECIMAL(19, 8), nullable=False)
    fiat_rate = Column("fiat_rate", DECIMAL(19, 8), nullable=False)
    created_at = Column("created_at", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow(), index=True)

class CryptoFiatExchangeRates(Base):
    __tablename__ = "crypto_fiat_rates"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    crypto_symbol = Column("crypto_symbol", VARCHAR(100), nullable=False)
    fiat_symbol = Column("fiat_symbol", VARCHAR(100), nullable=False)
    crypto_rate = Column("crypto_rate", DECIMAL(19, 8), nullable=False)
    fiat_rate = Column("fiat_rate", DECIMAL(19, 8), nullable=False)
    from_date = Column("from_date", TIMESTAMP(timezone=False), nullable=False)
    to_date = Column("to_date", TIMESTAMP(timezone=False), nullable=True)
    created_at = Column("created_at", TIMESTAMP(timezone=False), nullable=True, default=datetime.utcnow())