from utility.infrastructure.repository.base_repository import BaseRepository
from utility.infrastructure.models import HistoricalCryptoFiatExchangeRates as Rate
from sqlalchemy import and_, func
from decimal import Decimal


class HistoricalCryptoFiatRates(BaseRepository):
    def get_max_rates(self, crypto_symbol, fiat_symbol, limit, multiplier):
        try:
            result = self.session.query(func.max(Rate.crypto_rate).label("max")).filter(
                and_(Rate.crypto_symbol == crypto_symbol, Rate.fiat_symbol == fiat_symbol)).order_by(
                Rate.id.desc()).limit(limit).first()

            self.session.commit()
            if result is not None and result.max is not None:
                return result.max * Decimal(multiplier)
            else:
                return None
        except Exception as e:
            self.session.rollback()
            raise e
