from deployer.config import HAAS_DAEMON_BASE_URL


def get_daemon_endpoint(org_id: str, service_id: str) -> str:
    return f"https://{org_id}-{service_id}-testnet.{HAAS_DAEMON_BASE_URL}"
