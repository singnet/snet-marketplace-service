import json
import unittest

from utility.application.handlers.crypto_fiat_handler import calculate_latest_agi_rate, get_agi_fiat_rate, \
    get_agi_usd_rate
from utility.infrastructure.repository.crypto_fiat_rate import CryptoFiatRates
from utility.infrastructure.repository.historical_crypto_fiat_rate import HistoricalCryptoFiatRates
from utility.config import CRYPTO_FIAT_CONVERSION


class TestAGIUSDConversion(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_agi_usd_rate(self):
        crypto = 'AGI'
        fiat = 'USD'

        event = {}
        context = None
        get_agi_usd_rate(event=event, context=context)

        limit = CRYPTO_FIAT_CONVERSION['LIMIT']
        multiplier = CRYPTO_FIAT_CONVERSION['MULTIPLIER']

        rate = HistoricalCryptoFiatRates().get_max_rates(crypto_symbol=crypto, fiat_symbol=fiat, limit=limit,
                                                         multiplier=multiplier)
        self.assertGreaterEqual(rate, 0)

    def test_calculate_latest_agi_rate(self):
        crypto = 'AGI'
        fiat = 'USD'

        event = {}
        context = None
        calculate_latest_agi_rate(event=event, context=context)

        rate = CryptoFiatRates().get_latest_rate(crypto_symbol=crypto, fiat_symbol=fiat)
        self.assertGreaterEqual(rate.crypto_rate, 0)

    def test_invalid_crytpo_rate_cogs_conversion(self):
        crypto = 'AGI'
        fiat = 'INR'

        event = {}
        context = None
        get_agi_usd_rate(event=event, context=context)

        limit = CRYPTO_FIAT_CONVERSION['LIMIT']
        multiplier = CRYPTO_FIAT_CONVERSION['MULTIPLIER']

        rate = HistoricalCryptoFiatRates().get_max_rates(crypto_symbol=crypto, fiat_symbol=fiat, limit=limit,
                                                         multiplier=multiplier)

        self.assertEqual(rate, None)

    def test_invalid_agi_fiat_rate(self):
        crypto = 'AGI'
        fiat = 'INR'

        event = {}
        context = None
        calculate_latest_agi_rate(event=event, context=context)

        rate = CryptoFiatRates().get_latest_rate(crypto_symbol=crypto, fiat_symbol=fiat)
        self.assertEqual(rate, None)

    def test_get_agi_fiat_rate(self):
        event = {"pathParameters": {"currency": "USD"}, "queryStringParameters": {"amount": "100"}}
        response = get_agi_fiat_rate(event=event, context=None)

        print(response)

        assert (response["statusCode"] == 200)
        response_body = json.loads(response["body"])
        assert (response_body["status"] == "success")
        self.assertGreaterEqual(float(response_body["data"]["amount_in_agi"]), 0)
