import re
import json
from datetime import datetime as dt
from datetime import timedelta
from urllib.request import Request, urlopen, ssl, socket
from common.utils import Utils
from service_status.config import REGION_NAME, NOTIFICATION_ARN, SLACK_HOOK, NETWORKS, NETWORK_ID, \
    CERTIFICATION_EXPIRATION_THRESHOLD
from common.boto_utils import BotoUtils
from common.utils import Utils
from common.logger import get_logger

logger = get_logger(__name__)
boto_util = BotoUtils(region_name=REGION_NAME)
util = Utils()
NETWORK_NAME = NETWORKS[NETWORK_ID]["name"]
CERT_EXP_EMAIL_NOTIFICATION_MSG = \
    "<html><head></head><body><div><p>Hello,</p><p>Your certificates for service %s under organization " \
    "%s for the %s network are about to expire in %s days. Please take immediate action to renew them.</p>" \
    "<p>Endpoint: %s</p><br /> <br /><p>" \
    "<em>Please do not reply to the email for any enquiries for any queries please email at " \
    "cs-marketplace@singularitynet.io.</em></p><p>Warmest regards, <br />SingularityNET Marketplace " \
    "Team</p></div></body></html>"
CERT_EXP_EMAIL_NOTIFICATION_SUBJ = "Certificates are about to expire for service %s for %s network."
CERT_EXP_SLACK_NOTIFICATION_MSG = \
    "Certificates for service %s under organization %s for the %s network are about to expire in %s days."
NO_OF_ENDPOINT_TO_TEST_LIMIT = 5


class MonitorService:

    def _get_service_endpoint_data(self, limit):
        query = "SELECT row_id, org_id, service_id, endpoint, is_available, failed_status_count FROM service_endpoint WHERE " \
                "next_check_timestamp < UTC_TIMESTAMP AND endpoint not regexp %s AND (org_id,service_id) IN (SELECT org_id, service_id FROM service WHERE service.is_curated=1) ORDER BY last_check_timestamp ASC"
        if limit is not None:
            query = query + " LIMIT %s"
            result = self.repo.execute(query, [self.rex_for_pb_ip, limit])
        else:
            result = self.repo.execute(query, [self.rex_for_pb_ip])
        if result is None or result == []:
            logger.info("Unable to find services.")
        return result

    @staticmethod
    def _send_email_notification(recipients, certificate_expiration_notification_subject,
                                 certificate_expiration_notification_message):
        for recipient in recipients:
            send_notification_payload = {"body": json.dumps({
                "message": certificate_expiration_notification_message,
                "subject": certificate_expiration_notification_subject,
                "notification_type": "support",
                "recipient": recipient})}
            boto_util.invoke_lambda(lambda_function_arn=NOTIFICATION_ARN, invocation_type="RequestResponse",
                                    payload=json.dumps(send_notification_payload))
            logger.info(f"email_sent to {recipient}")

    def _valid_url(self, url):
        search_count = re.subn(self.rex_for_pb_ip, "", url)[1]
        if search_count == 0:
            return True
        return False

    @staticmethod
    def _is_https_endpoint(endpoint):
        if endpoint[:4].lower() == "http" and endpoint[:5].lower() != "https":
            return False
        return True

    @staticmethod
    def _send_slack_notification(slack_message):
        util.report_slack(slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)

    def _get_service_provider_email(self, org_id, service_id=None):
        emails = []
        query_response = self.repo.execute("SELECT contributors FROM service_metadata WHERE org_id = %s AND "
                                           "service_id = %s", [org_id, service_id])
        if len(query_response) == 0:
            logger.info(f"Org Id {org_id} is not present.")
            return None
        contacts = json.loads(query_response[0].get("contributors", '[]'))
        for contact in contacts:
            email_id = contact.get("email_id", None)
            if email_id is not None:
                emails.append(email_id)
        return emails

    def _update_next_service_health_check_timestamp(self, next_check_timestamp, org_id, service_id):
        query_response = self.repo.execute(
            "UPDATE service_endpoint SET next_check_timestamp = %s WHERE org_id = %s AND service_id = %s",
            [next_check_timestamp, org_id, service_id])
        if query_response[0] > 0:
            return "We will trigger a health check immediately."
        return "Unable to reset next health check time."


class MonitorServiceCertificate(MonitorService):
    def __init__(self, repo):
        self.repo = repo
        self.route = "/encoding"
        self.obj_util = Utils()
        # regex helps to check url is localhost or external address.
        self.rex_for_pb_ip = "^(http://)*(https://)*127.0.0.1|^(http://)*(https://)*localhost|^(http://)*" \
                             "(https://)*192.|^(http://)*(https://)*172.|^(http://)*(https://)*10."

    def notify_service_contributors_for_certificate_expiration(self):
        service_endpoint_data = self._get_service_endpoint_data(limit=None)
        for record in service_endpoint_data:
            org_id = record["org_id"]
            service_id = record["service_id"]
            endpoint = record["endpoint"]
            expiration_date = self._get_certification_expiration_date_for_given_service(endpoint=endpoint)
            days_left_for_expiration = (expiration_date - dt.utcnow()).days
            if days_left_for_expiration < CERTIFICATION_EXPIRATION_THRESHOLD:
                self._send_notification_for_certificate_expiration(org_id=org_id, service_id=service_id,
                                                                   endpoint=endpoint,
                                                                   days_left_for_expiration=days_left_for_expiration)

    def _send_notification_for_certificate_expiration(self, org_id, service_id, endpoint, days_left_for_expiration):

        certificate_expiration_notification_subject = \
            self._get_certificate_expiration_email_notification_subject(org_id=org_id, service_id=service_id,
                                                                        endpoint=endpoint)
        certificate_expiration_notification_message = \
            self._get_certificate_expiration_email_notification_message(
                org_id=org_id, service_id=service_id, endpoint=endpoint,
                days_left_for_expiration=days_left_for_expiration)

        recipients = self._get_service_provider_email(org_id=org_id, service_id=service_id)
        self._send_email_notification(
            certificate_expiration_notification_subject=certificate_expiration_notification_subject,
            certificate_expiration_notification_message=certificate_expiration_notification_message,
            recipients=recipients)
        slack_message = self._get_certificate_expiration_slack_notification_message(
            org_id=org_id, service_id=service_id, endpoint=endpoint, days_left_for_expiration=days_left_for_expiration)
        self._send_slack_notification(slack_message=slack_message)

    def _get_certification_expiration_date_for_given_service(self, endpoint):
        endpoint = endpoint.lstrip()
        if self._valid_url(url=endpoint):
            if self._is_https_endpoint(endpoint):
                endpoint = self.obj_util.remove_http_https_prefix(url=endpoint)
                hostname = endpoint.split(":")[0]
                port = endpoint.split(":")[1]
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port)) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        data = json.dumps(ssock.getpeercert())
                        expiration_date = json.loads(data)["notAfter"]
                        return dt.strptime(expiration_date, "%b %d %H:%M:%S %Y %Z")

    @staticmethod
    def _get_certificate_expiration_email_notification_subject(org_id, service_id, endpoint):
        return CERT_EXP_EMAIL_NOTIFICATION_SUBJ % (service_id, NETWORK_NAME)

    @staticmethod
    def _get_certificate_expiration_email_notification_message(org_id, service_id, endpoint, days_left_for_expiration):
        return CERT_EXP_EMAIL_NOTIFICATION_MSG % (service_id, org_id, NETWORK_NAME, days_left_for_expiration, endpoint)

    @staticmethod
    def _get_certificate_expiration_slack_notification_message(org_id, service_id, endpoint, days_left_for_expiration):
        return CERT_EXP_SLACK_NOTIFICATION_MSG % (service_id, org_id, NETWORK_NAME, days_left_for_expiration, endpoint)


class MonitorServiceHealth(MonitorService):
    def __init__(self, repo):
        self.repo = repo

    def reset_next_service_health_check_timestamp(self, org_id, service_id):
        response = self._update_next_service_health_check_timestamp(dt.utcnow(), org_id, service_id)
        return response
