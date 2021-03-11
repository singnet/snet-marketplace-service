import requests

from common.logger import get_logger
from utility.infrastructure.repository.historical_crypto_fiat_rate import HistoricalCryptoFiatRates
from utility.infrastructure.repository.crypto_fiat_rate import CryptoFiatRates
from utility.infrastructure.models import HistoricalCryptoFiatExchangeRates, CryptoFiatExchangeRates
from utility.config import CRYPTO_FIAT_CONVERSION, SLACK_HOOK
from datetime import datetime
from common.utils import Utils
from utility.services.secrets_manager import get_cmc_secret

rates = HistoricalCryptoFiatRates()

logger = get_logger(__name__)


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


def derive_new_crypto_rate(crypto, fiat):
    try:
        current_rate = convert_crypto_to_fiat(crypto=crypto, fiat=fiat)
        recent_max_rate = HistoricalCryptoFiatRates().get_max_rates(crypto_symbol=crypto, fiat_symbol=fiat,
                                                                    limit=CRYPTO_FIAT_CONVERSION['LIMIT'],
                                                                    multiplier=CRYPTO_FIAT_CONVERSION['MULTIPLIER'])
        recent_max_rate = float(recent_max_rate)
        current_rate = float(current_rate)

        percentage_in_price_change = get_change(current=current_rate, previous=recent_max_rate)
        if percentage_in_price_change >= CRYPTO_FIAT_CONVERSION['RATE_THRESHOLD']:
            today = datetime.today()
            latest_rate = CryptoFiatExchangeRates(fiat_symbol=fiat, crypto_symbol=crypto, crypto_rate=recent_max_rate,
                                                  fiat_rate=1, from_date=today)
            CryptoFiatRates().update_rate(crypto_symbol=crypto, fiat_symbol=fiat, to_date=today, item=latest_rate)
        else:
            Utils().report_slack(
                "{crypto}-{fiat} didn't update as the change in percentage is {percentage_in_price_change}. Recent "
                "max rate: {recent_max_rate}",
                SLACK_HOOK)

    except Exception as e:
        logger.error(f"Failed while updating latest AGI rate {e}")
        raise e


def get_cogs_amount(crypto, fiat, fiat_rate):
    try:
        rate = CryptoFiatRates().get_latest_rate(crypto_symbol=crypto, fiat_symbol=fiat)
        if rate is not None:
            return round((1 / rate.crypto_rate) * fiat_rate)
    except Exception as e:
        logger.error(f"Failed to get rates for {crypto}-{fiat} :: Error {e}")
        raise e


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        change = (abs(current - previous) / previous) * 100.0
        return round(change, 2)
    except ZeroDivisionError:
        return 0
