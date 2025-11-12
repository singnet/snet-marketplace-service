import hashlib

from deployer.config import HAAS_DAEMON_BASE_URL


def get_daemon_endpoint(org_id: str, service_id: str) -> str:
    org_service = f"{org_id}-{service_id}"
    hash_org_service = hashlib.sha256(org_service.encode()).hexdigest()

    return f"https://{hash_org_service}.{HAAS_DAEMON_BASE_URL}"
