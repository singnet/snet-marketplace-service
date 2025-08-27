import json
from datetime import datetime
from enum import Enum
from typing import Tuple

import requests
from requests.auth import HTTPBasicAuth

from common.logger import get_logger
from deployer.config import (
    HAAS_BASE_URL,
    HAAS_LOGIN,
    HAAS_PASSWORD,
    HAAS_REGISTRY,
    HAAS_REG_REPO,
    HAAS_BASE_IMAGE,
)


logger = get_logger(__name__)


class HaaSDaemonStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"


class HaaSClientError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Error while interacting with HaaS: {message}")


class HaaSClient:
    def __init__(self):
        self.auth = HTTPBasicAuth(HAAS_LOGIN, HAAS_PASSWORD)

    def start_daemon(
        self,
        org_id: str,
        service_id: str,
        daemon_config: dict,
    ):
        path = HAAS_BASE_URL + "/v1/daemon/create"
        request_data = {
            "registry": HAAS_REGISTRY,
            "reg_repo": HAAS_REG_REPO,
            "org": org_id,
            "service": service_id,
            "daemon_group": daemon_config["daemon_group"],
            "service_class": daemon_config["service_class"],
            "service_endpoint": daemon_config["service_endpoint"],
            "base_image": HAAS_BASE_IMAGE,
            "payment_channel_storage_type": daemon_config["payment_channel_storage_type"],
        }
        if "service_credentials" in daemon_config:
            request_data["service_credentials"] = daemon_config["service_credentials"]

        try:
            result = requests.post(path, data=request_data, auth=self.auth)
            if not result.ok:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def delete_daemon(self, org_id: str, service_id: str):
        path = HAAS_BASE_URL + "/v1/daemon/delete"
        try:
            result = requests.post(
                path,
                data={
                    "registry": HAAS_REGISTRY,
                    "reg_repo": HAAS_REG_REPO,
                    "org": org_id,
                    "service": service_id,
                },
                auth=self.auth,
            )
            if not result.ok:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def redeploy_daemon(
        self,
        org_id: str,
        service_id: str,
        daemon_config: dict,
    ):
        path = HAAS_BASE_URL + "/v1/daemon/redeploy"
        request_data = {
            "registry": HAAS_REGISTRY,
            "reg_repo": HAAS_REG_REPO,
            "org": org_id,
            "service": service_id,
            "daemon_group": daemon_config["daemon_group"],
            "service_class": daemon_config["service_class"],
            "service_endpoint": daemon_config["service_endpoint"],
            "base_image": HAAS_BASE_IMAGE,
            "payment_channel_storage_type": daemon_config["payment_channel_storage_type"],
        }
        if "service_credentials" in daemon_config:
            request_data["service_credentials"] = daemon_config["service_credentials"]

        try:
            result = requests.post(path, data=request_data, auth=self.auth)
            if not result.ok:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def check_daemon(
        self, org_id: str, service_id: str
    ) -> Tuple[HaaSDaemonStatus, datetime | None]:
        path = HAAS_BASE_URL + "/v1/daemon/check" + f"?org={org_id}&service={service_id}"
        try:
            result = requests.get(path, auth=self.auth)
            if result.ok:
                started_at = datetime.fromisoformat(
                    json.loads(result.json())[0]["running"]["startedAt"]
                )
                return HaaSDaemonStatus.UP, started_at
            elif result.status_code == 400:
                return HaaSDaemonStatus.DOWN, None
            else:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def get_public_key(self) -> str:
        path = HAAS_BASE_URL + "/v1/auth/public-key"
        try:
            result = requests.get(path, auth=self.auth)
            if result.ok:
                return json.loads(result.json())["public_key"]
            else:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))
