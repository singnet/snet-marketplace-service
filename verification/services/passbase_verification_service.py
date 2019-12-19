import requests

from verification.config import PASSBASE_BASE_URL, PASSBASE_API_SECRET
from common.constant import StatusCode


class PassbaseVerificationService:
    def get_all_authentications(self, limit=None, offset=None, from_created_at=None, to_created_at=None):
        url = f"{PASSBASE_BASE_URL}authentications/"
        headers = {"Content-Type": "application/json",
                   "Authorization": f"APIKEY {PASSBASE_API_SECRET}"}
        params = {limit: limit, offset: offset,
                  from_created_at: from_created_at, to_created_at: to_created_at}
        enhanced_params = {k: v for (k, v) in params.items() if v is not None}

        request = requests.get(url=url, headers=headers,
                               params=enhanced_params)

        status = request.status_code
        response = request.json()

        if (status != StatusCode.OK):
            raise Exception(response)

        return response
