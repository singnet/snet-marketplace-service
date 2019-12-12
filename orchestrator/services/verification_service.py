import requests

from orchestrator.config import TRULIOO_BASE_URL, TRULIOO_API_KEY
from common.constant import StatusCode

class VerificationService:


    def get_fields(self, configuration_name, country_code):
        url = f"{TRULIOO_BASE_URL}configuration/v1/fields/{configuration_name}/{country_code}"
        headers = {"x-trulioo-api-key": TRULIOO_API_KEY}
        request = requests.get(url=url, headers=headers)

        status = request.status_code;
        response = request.json();

        if status != StatusCode.OK:
            raise Exception(response)

        return response;

if __name__ == '__main__':
    VerificationService().get_fields("Identity Verification", "AU")