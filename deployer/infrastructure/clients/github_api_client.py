import time

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import jwt

from deployer.config import GITHUB_PRIVATE_KEY, GITHUB_APP_ID, JWT_EXPIRATION_IN_MINUTES


class GithubAPIClientError(Exception):
    def __init__(self, message):
        super().__init__(f"Github API Client error: {message}")


class GithubAPIClient:
    def __init__(self):
        pass

    def _generate_jwt(self) -> str:
        private_key = serialization.load_pem_private_key(
            GITHUB_PRIVATE_KEY.encode('utf-8'),
            password = None,
            backend = default_backend()
        )

        current_time = int(time.time())
        payload = {
            "iat": current_time,
            "exp": current_time + (60 * JWT_EXPIRATION_IN_MINUTES),
            "iss": GITHUB_APP_ID
        }

        return jwt.encode(payload, private_key, algorithm="RS256")

    def check_repo_installation(self, account_name: str, repository_name: str):
        try:
            token = self._generate_jwt()

            url = f"https://api.github.com/repos/{account_name}/{repository_name}/installation"
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                raise GithubAPIClientError(f"Error checking installation: status code - {response.status_code}, text - {response.text}")
        except Exception as e:
            raise GithubAPIClientError(f"Error checking installation: {e}")
