import json
import re
from datetime import datetime as dt
from datetime import timedelta

import grpc
from grpc_health.v1 import health_pb2 as heartb_pb2
from grpc_health.v1 import health_pb2_grpc as heartb_pb2_grpc

from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import Utils
from service_status.config import REGION_NAME, NOTIFICATION_ARN, SLACK_HOOK, NETWORKS, NETWORK_ID, \
    MAXIMUM_INTERVAL_IN_HOUR, MINIMUM_INTERVAL_IN_HOUR
from service_status.constant import SRVC_STATUS_GRPC_TIMEOUT, LIMIT

logger = get_logger(__name__)
boto_util = BotoUtils(region_name=REGION_NAME)
util = Utils()
NETWORK_NAME = NETWORKS[NETWORK_ID]["name"]


class ServiceStatus:
    def __init__(self, repo, net_id):
        self.repo = repo
        self.route = "/encoding"
        self.rex_for_pb_ip = "^(http://)*(https://)*127.0.0.1|^(http://)*(https://)*localhost|^(http://)*(https://)*192.|^(http://)*(https://)*172.|^(http://)*(https://)*10."
        self.obj_util = Utils()
        self.net_id = net_id

    def _get_service_status(self, url, secure=True):
        try:
            if secure:
                channel = grpc.secure_channel(
                    url, grpc.ssl_channel_credentials())
            else:
                channel = grpc.insecure_channel(url)

            stub = heartb_pb2_grpc.HealthStub(channel)
            response = stub.Check(heartb_pb2.HealthCheckRequest(
                service=""), timeout=SRVC_STATUS_GRPC_TIMEOUT)
            if response is not None and response.status == 1:
                logger.info(response.status)
                return 1, "", ""
            return 0, "", ""
        except Exception as e:
            logger.info(f"error in making grpc call::url: {url}, |error: {e}")
            logger.info(f"error : {e.args}")
            return 0, e.args[0].details, e.args[0].debug_error_string

    def _ping_url(self, url):
        search_count = re.subn(self.rex_for_pb_ip, "", url)[1]
        if search_count == 0:
            secure = True
            if url[:4].lower() == "http" and url[:5].lower() != "https":
                secure = False
            url = self.obj_util.remove_http_https_prefix(url=url)
            return self._get_service_status(url=url, secure=secure)
        return 0, "", ""

    def _get_service_endpoint_data(self):
        query = "SELECT row_id, org_id, service_id, endpoint, is_available, failed_status_count FROM service_endpoint WHERE " \
                "next_check_timestamp < UTC_TIMESTAMP AND endpoint not regexp %s ORDER BY last_check_timestamp ASC " \
                "LIMIT %s"
        result = self.repo.execute(query, [self.rex_for_pb_ip, LIMIT])
        if result is None or result == []:
            logger.info("Unable to find services.")
        return result

    def _update_service_status_parameters(self, status, next_check_timestamp, failed_status_count, row_id):
        update_query = "UPDATE service_endpoint SET is_available = %s, last_check_timestamp = current_timestamp, " \
                       "next_check_timestamp = %s, failed_status_count = %s WHERE row_id = %s "
        response = self.repo.execute(update_query, [status, next_check_timestamp, failed_status_count, row_id])
        return response

    def _update_service_status_stats(self, org_id, service_id, old_status, status):
        previous_state = "UP" if (old_status == 1) else "DOWN"
        current_state = "UP" if (status == 1) else "DOWN"

        try:
            insert_query = "insert into service_status_stats " \
                           "(org_id, service_id, previous_state, current_state, row_created, row_updated) " \
                           "values (%s, %s, %s, %s, %s, %s)"
            self.repo.execute(insert_query, [org_id, service_id, previous_state, current_state,
                                             dt.utcnow(), dt.utcnow()])
        except Exception as e:
            logger.info(f"error in inserting service status stats, |error: {e}")
        return

    def update_service_status(self):
        service_endpoint_data = self._get_service_endpoint_data()
        rows_updated = 0
        for record in service_endpoint_data:
            status, error_details, debug_error_string = self._ping_url(record["endpoint"])
            logger.info(f"error_details: {error_details}")
            logger.info(f"debug_error_string: {debug_error_string}")
            old_status = int.from_bytes(record["is_available"], "big")
            failed_status_count = self._calculate_failed_status_count(
                current_status=status, old_status=old_status,
                old_failed_status_count=record["failed_status_count"])
            next_check_timestamp = self._calculate_next_check_timestamp(failed_status_count=failed_status_count)
            query_data = self._update_service_status_parameters(status=status,
                                                                next_check_timestamp=next_check_timestamp,
                                                                failed_status_count=failed_status_count,
                                                                row_id=record["row_id"])
            if old_status != status:
                self._update_service_status_stats(record["org_id"], record["service_id"], old_status, status)

            if status == 0:
                org_id = record["org_id"]
                service_id = record["service_id"]
                recipients = self._get_service_provider_email(org_id=org_id, service_id=service_id)
                self._send_notification(org_id=org_id, service_id=service_id, recipients=recipients,
                                        endpoint=record["endpoint"], error_details=error_details,
                                        debug_error_string=debug_error_string)
            rows_updated = rows_updated + query_data[0]
        logger.info(f"no of rows updated: {rows_updated}")

    def _calculate_failed_status_count(self, current_status, old_status, old_failed_status_count):
        if current_status == old_status == 0:
            return old_failed_status_count + 1
        return 1

    def _calculate_next_check_timestamp(self, failed_status_count):
        time_delta_in_hours = MINIMUM_INTERVAL_IN_HOUR * (2 ** (failed_status_count - 1))
        if time_delta_in_hours > MAXIMUM_INTERVAL_IN_HOUR:
            time_delta_in_hours = MAXIMUM_INTERVAL_IN_HOUR
        next_check_timestamp = dt.utcnow() + timedelta(hours=time_delta_in_hours)
        return next_check_timestamp

    def _valid_email(self, email):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if re.search(regex, email):
            return True
        return False

    def _send_notification(self, org_id, service_id, recipients, endpoint, error_details, debug_error_string):
        slack_message = self._get_slack_message(org_id=org_id, service_id=service_id, endpoint=endpoint,
                                                recipients=recipients, error_details=error_details,
                                                debug_error_string=debug_error_string)
        util.report_slack(slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)
        for recipient in recipients:
            if recipient is None:
                logger.info(f"Email Id is not present for Org Id: {org_id} and Service Id: {service_id}")
            else:
                if self._valid_email(email=recipient):
                    self._send_email_notification(org_id=org_id, service_id=service_id, recipient=recipient,
                                                  endpoint=endpoint)
                else:
                    logger.info(f"Invalid email_id: {recipient}")

    def _get_slack_message(self, org_id, service_id, endpoint, recipients, error_details, debug_error_string):
        slack_message = f"```Alert!\n\nService {service_id} under organization {org_id} is down for {NETWORK_NAME} " \
                        f"network.\nEndpoint: {endpoint}\nError Details: {error_details}\nDebug Error String: " \
                        f"{debug_error_string}\nContributors: {recipients}  \n\nFor any queries please email at " \
                        f"cs-marketplace@singularitynet.io. \n\nWarmest regards, \nSingularityNET Marketplace Team```"
        return slack_message

    def _send_email_notification(self, org_id, service_id, recipient, endpoint):
        network_name = NETWORKS[NETWORK_ID]["name"]
        send_notification_payload = {"body": json.dumps({
            "message": f"<html><head></head><body><div><p>Hello,</p><p>Your service {service_id} under organization "
                       f"{org_id} is down.</p><p>Please click the below URL to update service status on priority. <br/> "
                       f"<a href='https://{network_name}-marketplace.singularitynet.io/service-status/org/{org_id}/service/{service_id}/health/reset'>"
                       f"https://{network_name}-marketplace.singularitynet.io/service-status/org/{org_id}/service/{service_id}/health/reset"
                       f"</a></p><br /><p><em>Please do not reply to the email for any enquiries for any queries please "
                       f"email at cs-marketplace@singularitynet.io. </em></p><p>Warmest regards, <br />"
                       f"SingularityNET Marketplace Team</p></div></body></html>",
            "subject": f"Your service {service_id} is down for {NETWORK_NAME} network.",
            "notification_type": "support",
            "recipient": recipient})}
        boto_util.invoke_lambda(lambda_function_arn=NOTIFICATION_ARN, invocation_type="RequestResponse",
                                payload=json.dumps(send_notification_payload))

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
