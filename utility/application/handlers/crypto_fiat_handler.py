from utility.services.crypto_to_fiat import convert_crypto_to_fiat, derive_new_agi_rate, get_cogs_amount
from datetime import datetime, timedelta
from common.logger import get_logger

logger = get_logger(__name__)

def get_agi_usd_rate(event, context):
    logger.info("Received request for AGI-USD rate")
    convert_crypto_to_fiat(crypto='AGI', fiat='USD')

if __name__ == '__main__':
    a = get_cogs_amount(crypto_symbol='AGI',fiat_symbol='USD', fiat_rate=4)
    # print(a)
    # event = {}
    # convert_crypto_to_fiat(crypto='AGI', fiat='USD')
    # start_date = datetime.today()
    # end_date = datetime.today() - timedelta(days=7)
    # amt = derive_new_agi_rate(crypto_symbol='AGI',fiat_symbol='USD')
    print(a)