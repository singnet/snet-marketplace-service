from service_status.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from common.repository import Repository
from common.utils import Utils
from common.utils import handle_exception_with_slack_notification
from common.logger import get_logger
from service_status.service_status import ServiceStatus
from service_status.monitor_service import MonitorServiceCertificate

obj_util = Utils()
db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
logger = get_logger(__name__)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def request_handler(event, context):
    service_status = ServiceStatus(repo=db, net_id=NETWORK_ID)
    service_status.update_service_status()


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def monitor_service_certificates_expiry_handler(event, context):
    monitor_status = MonitorServiceCertificate(repo=db, net_id=NETWORK_ID)
    monitor_status.notify_service_contributors_for_certificate_expiration()
    return "success"


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def monitor_service_health(event, context):
    return "success"


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def manage_monitor_service_health(event, context):
    return "success"


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def reset_service_health_failed_status_count(event, context):
    return "success"
