from deployer.config import HAAS_DAEMON_BASE_URL, HAAS_DAEMON_STAGE


def get_daemon_endpoint(org_id: str, service_id: str) -> str:
    return f"https://{org_id}-{service_id}-{HAAS_DAEMON_STAGE}.{HAAS_DAEMON_BASE_URL}"
