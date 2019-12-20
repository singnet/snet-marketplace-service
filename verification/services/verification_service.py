import requests

from verification.config import TRULIOO_BASE_URL, TRULIOO_API_KEY
from common.constant import StatusCode
from common.repository import Repository
from verification.config import NETWORK_ID, NETWORKS
from verification.dao.transaction_history_dao import TruliooTransactionHistoryDAO
from datetime import datetime as dt


class VerificationService:

    def __init__(self):
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
        self.trulioo_trxn_dao = TruliooTransactionHistoryDAO(repo=self.repo)

    def get_fields(self, configuration_name, country_code):
        url = f"{TRULIOO_BASE_URL}configuration/v1/fields/{configuration_name}/{country_code}"
        headers = {"x-trulioo-api-key": TRULIOO_API_KEY}
        request = requests.get(url=url, headers=headers)

        status = request.status_code
        response = request.json()

        if status != StatusCode.OK:
            raise Exception(response)

        return response

    def get_document_types(self, country_code):
        url = f"{TRULIOO_BASE_URL}configuration/v1/documentTypes/{country_code}"
        headers = {"x-trulioo-api-key": TRULIOO_API_KEY}
        request = requests.get(url=url, headers=headers)

        status = request.status_code
        response = request.json()

        if status != StatusCode.OK:
            raise Exception(response)

        return response

    def get_verification_transaction(self, payload):
        url = f"{TRULIOO_BASE_URL}/verifications/v1/verify"
        headers = {"x-trulioo-api-key": TRULIOO_API_KEY}
        response = requests.post(url=url, headers=headers, data=payload)
        if response.status_code == 200:
            transaction_data = response.json()
            self.trulioo_trxn_dao.insert_trulioo_transaction_data(
                transaction_id=transaction_data["TransactionID"],
                transaction_record_id=transaction_data["Record"]["TransactionRecordID"],
                country_code=transaction_data["CountryCode"], product_name=transaction_data["ProductName"],
                uploaded_date=transaction_data["UploadedDt"], record_status=transaction_data["Record"]["RecordStatus"])
            return transaction_data
        raise Exception("Unable to get verification transaction data.")
