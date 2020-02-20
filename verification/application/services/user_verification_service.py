import requests
from common.boto_utils import BotoUtils
from common.constant import StatusCode
from verification.config import JUMIO_BASE_URL, JUMIO_API_KEY, SUCCESS_REDIRECTION_DAPP_URL, \
    USER_REFERENCE_ID_NAMESPACE, REGION_NAME
from verification.infrastructure.repositories.user_verification_repository import UserVerificationRepository
from uuid import uuid4, uuid5
from verification.utils import get_user_reference_id_from_username
from verification.exceptions import UnableToInitiateException

user_verification_repo = UserVerificationRepository()


class UserVerificationService:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name=REGION_NAME)

    def initiate(self, username):
        transaction_id = uuid4().hex
        user_reference_id = get_user_reference_id_from_username(username)
        api_key = self.boto_utils.get_ssm_parameter(JUMIO_API_KEY)

        url = f"{JUMIO_BASE_URL}/initiate"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "content-length": 3495,
            "authorization": f"Basic {api_key}"
        }
        data = {
            "customerInternalReference": transaction_id,  # internal reference for the transaction.
            "userReference": user_reference_id,  # internal reference for the user.
            "successUrl": SUCCESS_REDIRECTION_DAPP_URL
        }
        request = requests.post(url=url, headers=headers, data=data)

        status = request.status_code
        response = request.json()
        if status != StatusCode.OK:
            raise UnableToInitiateException(response)

        user_verification_repo.add_transaction(transaction_id, user_reference_id)

        return response

    def submit(self, transaction_id, jumio_reference, error_code):
        user_verification_repo.update_jumio_reference(transaction_id, jumio_reference, error_code)
        return "OK"

    def complete(self, payload):
        verification_response = {
            "call_back_type": payload.callBackType,
            "jumio_reference": payload.jumioIdScanReference,
            "verification_status": payload.verificationStatus,
            "id_scan_status": payload.idScanStatus,
            "id_scan_source": payload.idScanSource,
            "transaction_date": payload.transactionDate,
            "callback_date": payload.callbackDate,
            "identity_verification": payload.identityVerification,
            "id_type": payload.idType,
        }
        user_verification_repo.complete_transaction(payload)
        return "OK"

    def get_status(self, username):
        user_reference_id = get_user_reference_id_from_username(username)
        status = user_verification_repo.get_status(user_reference_id)
        return status
