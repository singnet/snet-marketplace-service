import requests

from common.constant import StatusCode
from user_verification.config import JUMIO_BASE_URL, JUMIO_API_KEY
from user_verification.infrastructure.repositories.user_verification_repository import UserVerificationRepository

user_verification_repo = UserVerificationRepository()


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

    def callback(self, payload):
        # save the value from payload to DB
        verification_response = {
            "call_back_type": payload.callBackType,
            "jumio_id_scan_reference": payload.jumioIdScanReference,
            "verification_status": payload.verificationStatus,
            "id_scan_status": payload.idScanStatus,
            "id_scan_source": payload.idScanSource,
            "transaction_date": payload.transactionDate,
            "callback_date": payload.callbackDate,
            "identity_verification": payload.identityVerification,
            "id_type": payload.idType,
        }
        user_verification_repo.add_verification_response(payload)
        return "OK"
