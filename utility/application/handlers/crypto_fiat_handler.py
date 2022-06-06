from utility.services.crypto_to_fiat import convert_crypto_to_fiat, derive_new_crypto_rate, get_cogs_amount
from common.logger import get_logger
from common.utils import generate_lambda_response, validate_dict

logger = get_logger(__name__)
REQUIRED_KEYS_FOR_CURRENCY_TO_TOKEN_CONVERSION = ['pathParameters', 'queryStringParameters']

def get_agi_fiat_rate(event, context):
    logger.info("Received request for AGIX-USD rate {event}")
    try:
        valid_event = validate_dict(
            data_dict=event, required_keys=REQUIRED_KEYS_FOR_CURRENCY_TO_TOKEN_CONVERSION)
        if(valid_event):

            path_parameters = event["pathParameters"]
            query_string_parameters = event["queryStringParameters"]

            currency = path_parameters["currency"]
            amount = query_string_parameters["amount"]
            rate = get_cogs_amount(crypto='AGIX', fiat=currency, fiat_rate=amount)

            if rate is not None:
                conversion_data = {"base": currency, "amount": amount, "amount_in_agi": str(rate)}
                response = generate_lambda_response(200, {"status": "success", "data": conversion_data}, cors_enabled=True)
            else:
                response = generate_lambda_response(400,  "Failed to convert", cors_enabled=True)
        else:
            response = generate_lambda_response(400, "Bad Request", cors_enabled=True)
    except Exception as e:
        logger.info("Failed to response to AGIX-USD rate {e}")
        response = generate_lambda_response(400, "Bad Request", cors_enabled=True)
    return response

def get_agi_usd_rate(event, context):
    logger.info("Received request for AGIX-USD rate")
    convert_crypto_to_fiat(crypto='AGIX', fiat='USD')


def calculate_latest_agi_rate(event, context):
    logger.info("Received request for computing latest AGI rate")
    derive_new_crypto_rate(crypto='AGIX', fiat='USD')