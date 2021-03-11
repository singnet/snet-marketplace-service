from utility.services.crypto_to_fiat import convert_crypto_to_fiat, derive_new_crypto_rate
from common.logger import get_logger

logger = get_logger(__name__)


def get_agi_usd_rate(event, context):
    logger.info("Received request for AGI-USD rate")
    convert_crypto_to_fiat(crypto='AGI', fiat='USD')


def calculate_latest_agi_rate(event, context):
    logger.info("Received request for computing latest AGI rate")
    derive_new_crypto_rate(crypto='AGI', fiat='USD')
