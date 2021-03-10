import requests

from common.logger import get_logger
from utility.infrastructure.repository.historical_crypto_fiat_rate import HistoricalCryptoFiatRates
from utility.infrastructure.repository.crypto_fiat_rate import CryptoFiatRates
from utility.infrastructure.models import HistoricalCryptoFiatExchangeRates, CryptoFiatExchangeRates
from utility.config import CRYPTO_FIAT_CONVERSION, SLACK_HOOK
from datetime import datetime, timedelta
from common.utils import Utils
from utility.services.secrets_manager import get_cmc_secret

utils = Utils()
rates = HistoricalCryptoFiatRates()

logger = get_logger(__name__)
# utils.report_slack(f"got error : {response} \n {str(e)} \n for event : {event} ", SLACK_HOOK)


def cmc_rate_converter(crypto_symbol, fiat_symbol):
    try:
        URL = CRYPTO_FIAT_CONVERSION['COINMARKETCAP']['API_ENDPOINT'].format(
            fiat_symbol, crypto_symbol)
        headers = {'X-CMC_PRO_API_KEY': get_cmc_secret()}
        result = requests.get(url=URL, headers=headers)
        response = result.json()['data'][0]
        fiat_rate = response['amount']
        crypto_rate = response['quote'][fiat_symbol]['price']
        logger.info(f"rates_from_cmc response: {response}")
        return crypto_symbol, crypto_rate, fiat_rate, fiat_symbol
    except Exception as e:
        logger.error(f"Failed to retrieve exchange rate from CMC: {e}")
        raise e


# TODO: Create handler and call daily
def convert_crypto_to_fiat(crypto, fiat):
    if CRYPTO_FIAT_CONVERSION['EXCHANGE'] == 'COINMARKETCAP':

        crypto_symbol, crypto_rate, fiat_rate, fiat_symbol = cmc_rate_converter(crypto_symbol=crypto, fiat_symbol=fiat)

        rate = HistoricalCryptoFiatExchangeRates(fiat_symbol=fiat_symbol, crypto_symbol=crypto_symbol,
                                                 crypto_rate=crypto_rate, fiat_rate=fiat_rate)
        rates.add_item(item=rate)

        return crypto_rate
    else:
        logger.error(f"Invalid exchange in config")
        raise Exception('Invalid exchange')


# TODO: Create handler and call weekly
def derive_new_agi_rate(crypto_symbol, fiat_symbol):

    start_date = datetime.today()
    end_date = datetime.today() - timedelta(days=7)

    try:
        current_rate = CryptoFiatRates().get_latest_rate(crypto_symbol=crypto_symbol,fiat_symbol=fiat_symbol,fiat_unit=1).crypto_rate or convert_crypto_to_fiat(crypto=crypto_symbol, fiat=fiat_symbol)
        average_rate = HistoricalCryptoFiatRates().get_avg_crypto_rates_between_date(crypto_symbol, fiat_symbol, start_date, end_date,
                                                                    CRYPTO_FIAT_CONVERSION['MULTIPLIER'])

        latest_rate = CryptoFiatExchangeRates(fiat_symbol=fiat_symbol, crypto_symbol=crypto_symbol,
                                                    crypto_rate=average_rate, fiat_rate=1, from_date=start_date)

        # TODO: Add some formulae here

        CryptoFiatRates().update_rate(crypto_symbol=crypto_symbol, fiat_symbol=fiat_symbol, to_date=start_date, item=latest_rate)
        
    except Exception as e:
        logger.error(f"Failed while updating latest AGI rate {e}")
        raise(e)    
     


def get_cogs_amount(crypto_symbol, fiat_symbol, fiat_rate):
    try:
        rate = CryptoFiatRates().get_latest_rate(crypto_symbol=crypto_symbol, fiat_symbol=fiat_symbol)
        if rate is not None:
            return round((1/rate.crypto_rate) * fiat_rate)
        else:
            return False
    except Exception as e:
        logger.error(f"Failed to get rates for {crypto_symbol}-{fiat_symbol} :: Error {e}")
        raise(e)
