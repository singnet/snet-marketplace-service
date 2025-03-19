from service_status.config import NETWORKS, NETWORK_ID, SLACK_HOOK
from common.repository import Repository
from common.utils import Utils
from common.utils import handle_exception_with_slack_notification, generate_lambda_response
from common.logger import get_logger
from common.constant import StatusCode
from service_status.exceptions import BadRequestException
from service_status.service_status import ServiceStatus
from service_status.monitor_service import MonitorServiceCertificate, MonitorServiceHealth


obj_util = Utils()
db = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)
logger = get_logger(__name__)


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def request_handler(event, context):
    service_status = ServiceStatus(repo=db, net_id=NETWORK_ID)
    service_status.update_service_status()
    return "success"


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def monitor_service_certificates_expiry_handler(event, context):
    monitor_status = MonitorServiceCertificate(repo=db)
    monitor_status.notify_service_contributors_for_certificate_expiration()
    return "success"


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def monitor_service_health(event, context):
    return "success"


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def manage_monitor_service_health(event, context):
    return "success"


@handle_exception_with_slack_notification(logger=logger, NETWORK_ID=NETWORK_ID, SLACK_HOOK=SLACK_HOOK)
def reset_service_health_next_check_time(event, context):
    path_parameters = event["pathParameters"]
    if "org_id" not in path_parameters and "service_id" not in path_parameters:
        raise BadRequestException()
    monitor_status = MonitorServiceHealth(repo=db)
    response = monitor_status.reset_next_service_health_check_timestamp(path_parameters["org_id"],
                                                                        path_parameters["service_id"])
    return generate_lambda_response(
        StatusCode.OK,
        {"status": "success", "data": response, "error": {}}, cors_enabled=True
    )
