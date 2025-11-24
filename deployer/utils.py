from deployer.config import HAAS_DAEMON_BASE_URL, NETWORKS, NETWORK_ID


def get_daemon_endpoint(org_id: str, service_id: str) -> str:
    return f"https://{org_id}-{service_id}-{NETWORKS[NETWORK_ID]['name']}.{HAAS_DAEMON_BASE_URL}"
