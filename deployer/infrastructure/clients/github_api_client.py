import time
from typing import Tuple

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import jwt

from deployer.config import GITHUB_PRIVATE_KEY, GITHUB_APP_ID, JWT_EXPIRATION_IN_MINUTES


class GithubAPIClientError(Exception):
    def __init__(self, message):
        super().__init__(f"Github API Client error: {message}")


class GithubAPIClient:
    @staticmethod
    def __generate_jwt() -> str:
        private_key = serialization.load_pem_private_key(
            GITHUB_PRIVATE_KEY.encode("utf-8"), password=None, backend=default_backend()
        )

        current_time = int(time.time())
        payload = {
            "iat": current_time,
            "exp": current_time + (60 * JWT_EXPIRATION_IN_MINUTES),
            "iss": GITHUB_APP_ID,
        }

        return jwt.encode(payload, private_key, algorithm="RS256")

    @staticmethod
    def _get_installation(account_name: str, repository_name: str) -> Tuple[int, dict]:
        try:
            token = GithubAPIClient.__generate_jwt()

            url = f"https://api.github.com/repos/{account_name}/{repository_name}/installation"
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

            response = requests.get(url, headers=headers)

            return response.status_code, response.json()
        except Exception as e:
            raise GithubAPIClientError(f"Error getting installation: {e}")

    @staticmethod
    def check_repo_installation(account_name: str, repository_name: str) -> bool:
        status_code, response = GithubAPIClient._get_installation(account_name, repository_name)

        if status_code == 200:
            return True
        elif status_code == 404:
            return False
        else:
            raise GithubAPIClientError(
                f"Error checking installation: status code - {status_code}, body - {response}"
            )

    @staticmethod
    def get_installation_id(account_name: str, repository_name: str) -> str:
        status_code, response = GithubAPIClient._get_installation(account_name, repository_name)

        if status_code == 200:
            return response["id"]
        else:
            raise GithubAPIClientError(
                f"Error getting installation id: status code - {status_code}, body - {response}"
            )

    @staticmethod
    def make_commit_url(account_name: str, repository_name: str, commit_hash: str) -> str:
        return f"https://github.com/{account_name}/{repository_name}/commit/{commit_hash}"

    @staticmethod
    def make_repository_url(account_name: str, repository_name: str) -> str:
        return f"https://github.com/{account_name}/{repository_name}"
