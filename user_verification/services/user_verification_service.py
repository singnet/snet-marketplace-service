import requests

from user_verification.config import JUMIO_BASE_URL, JUMIO_API_KEY
from common.constant import StatusCode


class UserVerificationService:
    def __init__(self):
        self.request_headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "content-length": 3495,
            "authorization": f"Basic {JUMIO_API_KEY}"
        }

    def initiate(self, payload):
        url = f"{JUMIO_BASE_URL}/initiate"
        headers = self.request_headers
        request = requests.get(url, headers)

        status = request.status_code
        response = request.json()

        if status != StatusCode.OK:
            raise Exception(response)

        return response
