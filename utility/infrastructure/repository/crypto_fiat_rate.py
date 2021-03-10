from utility.infrastructure.repository.base_repository import BaseRepository
from utility.infrastructure.models import CryptoFiatExchangeRates as Rate
from sqlalchemy import and_, func


class CryptoFiatRates(BaseRepository):
    def get_latest_rate(self, crypto_symbol, fiat_symbol):
        try:

            result = self.session.query(Rate).filter(Rate.crypto_symbol == crypto_symbol, Rate.fiat_symbol == fiat_symbol).order_by(Rate.id.desc()).first()
            self.session.commit()

            if result is None:
                return None
            else:
                return result
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_rate(self, crypto_symbol, fiat_symbol, to_date, item):
        try:

            result = self.session.query(Rate).filter(Rate.crypto_symbol == crypto_symbol, Rate.fiat_symbol == fiat_symbol).order_by(Rate.id.desc()).first()
            result.to_date = to_date

            self.add_item(item=item)            
            self.session.commit()

            if result is None:
                return None
            else:
                return result
        except Exception as e:
            self.session.rollback()
            raise e
