from typing import Tuple, List, Union

import requests
from requests.auth import HTTPBasicAuth

from common.logger import get_logger
from deployer.config import (
    HAAS_BASE_URL,
    HAAS_LOGIN,
    HAAS_PASSWORD,
    HAAS_DAEMON_IMAGE,
    HAAS_DEPLOY_DAEMON_PATH,
    HAAS_DELETE_DAEMON_PATH,
    HAAS_GET_DAEMON_LOGS_PATH,
    HAAS_GET_PUBLIC_KEY_PATH,
    HAAS_DELETE_HOSTED_SERVICE_PATH,
    HAAS_GET_HOSTED_SERVICE_LOGS_PATH,
    HAAS_GET_CALL_EVENTS_PATH,
)
from deployer.constant import PeriodType, OrderType
from deployer.domain.schemas.haas_responses import GetCallEventsResponse

logger = get_logger(__name__)


class HaaSClientError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Error while interacting with HaaS: {message}")


class HaaSClient:
    def __init__(self):
        self.auth = HTTPBasicAuth(HAAS_LOGIN, HAAS_PASSWORD)

    # ========== DAEMON ==========

    def deploy_daemon(
        self,
        org_id: str,
        service_id: str,
        daemon_config: dict,
    ):
        url = HAAS_BASE_URL + HAAS_DEPLOY_DAEMON_PATH.format(org_id, service_id)

        request_data = {
            "daemonGroup": daemon_config["daemon_group"],
            "serviceClass": daemon_config["service_class"],
            "serviceEndpoint": daemon_config["service_endpoint"],
            "daemonImage": HAAS_DAEMON_IMAGE,
            "paymentChannelStorageType": daemon_config["payment_channel_storage_type"],
            "isServiceHosted": daemon_config["is_service_hosted"],
        }
        if "serviceCredentials" in daemon_config:
            request_data["service_credentials"] = daemon_config["service_credentials"]

        try:
            result = requests.post(url, json=request_data, auth=self.auth)
            if not result.ok:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def delete_daemon(self, org_id: str, service_id: str):
        url = HAAS_BASE_URL + HAAS_DELETE_DAEMON_PATH.format(org_id, service_id)

        try:
            result = requests.delete(url, auth=self.auth)
            if not result.ok:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def get_daemon_logs(self, org_id: str, service_id: str, tail: int = 200) -> List[str]:
        url = HAAS_BASE_URL + HAAS_GET_DAEMON_LOGS_PATH.format(org_id, service_id)
        url += f"tail={tail}"

        try:
            result = requests.get(url, auth=self.auth)
            if result.ok:
                return result.json()["data"]["logs"]
            else:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def get_public_key(self) -> str:
        url = HAAS_BASE_URL + HAAS_GET_PUBLIC_KEY_PATH

        try:
            result = requests.get(url, auth=self.auth)
            if result.ok:
                return result.json()["data"]["publicKey"]
            else:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    # ========== HOSTED SERVICE ==========

    def delete_hosted_service(self, org_id: str, service_id: str):
        url = HAAS_BASE_URL + HAAS_DELETE_HOSTED_SERVICE_PATH.format(org_id, service_id)

        try:
            result = requests.delete(url, auth=self.auth)
            if not result.ok:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    def get_hosted_service_logs(self, org_id: str, service_id: str, tail: int = 400) -> list:
        url = HAAS_BASE_URL + HAAS_GET_HOSTED_SERVICE_LOGS_PATH.format(org_id, service_id)
        url += f"tail={tail}"

        try:
            result = requests.get(url, auth=self.auth)
            if result.ok:
                return result.json()["data"]["logs"]
            else:
                raise HaaSClientError(result.text)
        except Exception as e:
            raise HaaSClientError(str(e))

    # ========== METRICS ==========

    def get_call_events(
        self,
        limit: int,
        page: int,
        order: OrderType,
        period: PeriodType,
        services: Union[List[Tuple[str, str]], Tuple[str, str], None] = None,
    ) -> GetCallEventsResponse:
        url = HAAS_BASE_URL + HAAS_GET_CALL_EVENTS_PATH

        if services is None:
            services = []
        elif isinstance(services, tuple):
            services = [services]
        request_services = []
        for service in services:
            request_services.append({"orgId": service[0], "serviceId": service[1]})
        request_body = {
            "services": request_services,
            "limit": limit,
            "page": page,
            "order": order.value,
            "period": period.value,
        }

        try:
            # TODO: configure the correct auth
            response = requests.post(url, json=request_body)
            if response.ok:
                return GetCallEventsResponse(**response.json())
            else:
                raise HaaSClientError(response.text)
        except Exception as e:
            raise HaaSClientError(str(e))
