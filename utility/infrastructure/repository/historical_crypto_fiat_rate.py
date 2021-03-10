from utility.infrastructure.repository.base_repository import BaseRepository
from utility.infrastructure.models import HistoricalCryptoFiatExchangeRates as Rate
from sqlalchemy import and_, func


class HistoricalCryptoFiatRates(BaseRepository):
    def get_avg_crypto_rates_between_date(self, crypto_symbol, fiat_symbol, start_date, end_date, multiplier):
        try:
            added_at = Rate.added_at

            result = self.session.query(func.avg(Rate.crypto_rate * multiplier).label("max")).filter(and_(added_at <= start_date, added_at >= end_date), and_(Rate.crypto_symbol==crypto_symbol, Rate.fiat_symbol == fiat_symbol)).one()

            self.session.commit()
            return result.max
        except Exception as e:
            self.session.rollback()
            raise e
