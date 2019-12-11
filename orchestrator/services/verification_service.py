import requests

from orchestrator.config import TRULIOO_BASE_URL, TRULIOO_API_KEY


class VerificationService:

    def get_fields(self, configuration_name, country_code):
        url = f"{TRULIOO_BASE_URL}configuration/v1/fields/{configuration_name}/{country_code}"
        headers = {"x-trulioo-api-key": TRULIOO_API_KEY}
        request = requests.get(url=url, headers=headers)

        status = request.status_code;
        response = request.json();

        if status != 200:
            raise Exception(response)

        return response;
