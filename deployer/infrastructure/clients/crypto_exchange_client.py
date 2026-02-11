import requests


class CryptoExchangeClientError(Exception):
    def __init__(self, name: str, message: str):
        super().__init__(f"Crypto Exchange ({name}) Client error: {message}")


class CryptoExchangeClient:
    def get_token_rate(self, token_symbol: str) -> float:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            query_params = {"symbols": token_symbol, "vs_currencies": "usd"}

            response = requests.get(url, params=query_params)

            return float(response.json()[token_symbol]["usd"])
        except Exception as e:
            raise CryptoExchangeClientError("coingecko", str(e))
