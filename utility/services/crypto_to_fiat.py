import requests

from common.logger import get_logger
from utility.infrastructure.repository.historical_crypto_fiat_rate import HistoricalCryptoFiatRates
from utility.infrastructure.repository.crypto_fiat_rate import CryptoFiatRates
from utility.infrastructure.models import HistoricalCryptoFiatExchangeRates, CryptoFiatExchangeRates
from utility.config import CRYPTO_FIAT_CONVERSION, SLACK_HOOK
from datetime import datetime
from common.boto_utils import BotoUtils
from common.utils import Utils

rates = HistoricalCryptoFiatRates()

logger = get_logger(__name__)
boto_client = BotoUtils(region_name='us-east-1')

def cmc_rate_converter(crypto_symbol, fiat_symbol):
    try:
        api_token = boto_client.get_parameter_value_from_secrets_manager(secret_name='COIN_MARKETPLACE_API_TOKEN')
        URL = CRYPTO_FIAT_CONVERSION['COINMARKETCAP']['API_ENDPOINT'].format(
            fiat_symbol, crypto_symbol)
        headers = {'X-CMC_PRO_API_KEY': api_token}
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

    latest_rate = convert_crypto_to_fiat(crypto=crypto, fiat=fiat)
    crypto_rate = get_latest_crypto_rate(crypto=crypto, fiat=fiat, fiat_rate=1)
    crypto_rate = float(crypto_rate)
    latest_rate = float(latest_rate)
    
    if latest_rate > crypto_rate:
        update_rate(crypto=crypto, fiat=fiat, latest_rate=latest_rate)
    else:

        derived_rate = HistoricalCryptoFiatRates().get_max_rates(crypto_symbol=crypto, fiat_symbol=fiat,
                                                                    limit=CRYPTO_FIAT_CONVERSION['LIMIT'],
                                                                    multiplier=CRYPTO_FIAT_CONVERSION['MULTIPLIER'])

        derived_rate = float(derived_rate)

        percentage_in_price_change = get_change(current=latest_rate, previous=derived_rate)

        if percentage_in_price_change >= CRYPTO_FIAT_CONVERSION['RATE_THRESHOLD']:
            update_rate(crypto=crypto, fiat=fiat, latest_rate=derived_rate)
        else:
            Utils().report_slack(
                    "{crypto}-{fiat} didn't update as the change in percentage is {percentage_in_price_change}. Recent "
                    "derived rate: {derived_rate}",
                    SLACK_HOOK)     

def get_latest_crypto_rate(crypto, fiat, fiat_rate):
    try:
        rate = CryptoFiatRates().get_latest_rate(crypto_symbol=crypto, fiat_symbol=fiat)
        if rate is None:
            return CRYPTO_FIAT_CONVERSION['CURRENT_AGI_USD_RATE']
        else:
            return round(rate.crypto_rate, 4)
    except Exception as e:
        logger.error(f"Failed to get rates for {crypto}-{fiat} :: Error {e}")
    return False

def get_cogs_amount(crypto, fiat, fiat_rate):
    try:
        rate = CryptoFiatRates().get_latest_rate(crypto_symbol=crypto, fiat_symbol=fiat)
        if rate is None:
            return CRYPTO_FIAT_CONVERSION['CURRENT_AGI_USD_RATE']
        else:
            rate = rate.crypto_rate
            return round((1 / float(rate)) * float(fiat_rate), 4)
    except Exception as e:
        logger.error(f"Failed to get rates for {crypto}-{fiat} :: Error {e}")
    return False

def update_rate(crypto,fiat,latest_rate):
    today = datetime.today()
    rate = CryptoFiatExchangeRates(fiat_symbol=fiat, crypto_symbol=crypto, crypto_rate=latest_rate,
                                                  fiat_rate=1, from_date=today)
    CryptoFiatRates().update_rate(crypto_symbol=crypto, fiat_symbol=fiat, to_date=today, item=rate)

def get_change(current, previous):
    if current == previous:
        return 0
    try:
        change = (abs(current - previous) / previous) * 100.0
        return round(change, 2)
    except ZeroDivisionError:
        return 0
