import unittest
import json
import grpc
from grpc_health.v1 import health_pb2 as heartb_pb2
from grpc_health.v1 import health_pb2_grpc as heartb_pb2_grpc
from unittest import TestCase
from datetime import datetime as dt
from datetime import timedelta

from common.constant import root_certificate
from service_status.handlers.monitor_service_handlers import monitor_service_certificates_expiry_handler, \
    reset_service_health_next_check_time
from unittest.mock import patch
from common.repository import Repository
from service_status.config import NETWORK_ID, NETWORKS


class TestMonitorService(TestCase):
    def setUp(self):
        self.repo = Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS)

    # @patch("service_status.monitor_service.MonitorServiceCertificate._get_service_endpoint_data")
    # @patch(
    #     "service_status.monitor_service.MonitorServiceCertificate._get_certification_expiration_date_for_given_service")
    # @patch("service_status.monitor_service.MonitorServiceCertificate._get_service_provider_email")
    # @patch("common.utils.Utils.report_slack")
    # @patch("service_status.monitor_service.MonitorServiceCertificate._send_email_notification")
    # def test_monitor_service_certificate_expiry_handler(
    #         self, _send_email_notification, report_slack, _get_service_provider_email,
    #         _get_certification_expiration_date_for_given_service,
    #         _get_service_endpoint_data):
    #     _get_service_endpoint_data.return_value = [
    #         {"endpoint": "https://dummy.com:9999", "org_id": "test_org_id", "service_id": "test_service"}]
    #     _get_certification_expiration_date_for_given_service.return_value = dt.utcnow() + timedelta(days=25)
    #     _get_service_provider_email.return_value = ["prashant@singularitynet.io"]
    #     report_slack.return_value = None
    #     _send_email_notification.return_value = None
    #     response = monitor_service_certificates_expiry_handler(event={}, context=None)
    #     assert (response == "success")

    # def test_reset_service_health_failed_status_count(self):
    #     self.tearDown()
    #     created_at = dt.utcnow() - timedelta(days=25)
    #     updated_at = dt.utcnow() - timedelta(hours=6)
    #     last_check_timestamp = dt.utcnow() - timedelta(hours=6)
    #     next_check_timestamp = dt.utcnow() + timedelta(hours=6)
    #     current_timestamp = dt.utcnow()
    #     org_id = "test_org_id"
    #     service_id = "test_service_id"
    #     self.repo.execute(
    #         "INSERT INTO service (row_id, org_id, service_id, service_path, ipfs_hash, is_curated, row_created, row_updated)"
    #         "VALUES(1, %s, %s, '', '', 0, %s, %s)",
    #         [org_id, service_id, created_at, updated_at]
    #     )
    #     self.repo.execute(
    #         "INSERT INTO service_endpoint (service_row_id, org_id, service_id, group_id, endpoint, is_available, "
    #         "last_check_timestamp, next_check_timestamp, failed_status_count, row_created, row_updated)"
    #         "VALUES(1, %s, %s, 'test_group_id', 'https://dummy.io', 0, %s, %s, 10, %s, %s)",
    #         [org_id, service_id, last_check_timestamp, next_check_timestamp, created_at, updated_at]
    #     )
    #     event = {
    #         "httpMethod": "GET",
    #         "pathParameters": {
    #             "org_id": org_id,
    #             "service_id": service_id}
    #     }
    #     response = reset_service_health_next_check_time(event=event, context=None)
    #     db_response = self.repo.execute(
    #         "SELECT next_check_timestamp FROM service_endpoint WHERE org_id = %s AND service_id = %s",
    #         [org_id, service_id])
    #     date_diff = (db_response[0]["next_check_timestamp"] - current_timestamp)
    #     assert ((date_diff.microseconds / 1000000) <= 2)
    #     assert (response["statusCode"] == 200)
    #     response_body = json.loads(response["body"])
    #     assert (response_body["data"] == "We will trigger a health check immediately.")

    def test_get_service_status(self, secure=True):
        url = "https://bh.singularitynet.io:7252"
        url = "138.197.215.173:5001"
        try:
            if secure:
                channel = grpc.secure_channel(
                    url, grpc.ssl_channel_credentials(root_certificates=root_certificate))
            else:
                channel = grpc.insecure_channel(url)

            stub = heartb_pb2_grpc.HealthStub(channel)
            response = stub.Check(heartb_pb2.HealthCheckRequest(
                service=""), timeout=10)
            if response is not None and response.status == 1:
                # logger.info(response.status)
                return 1
            return 0
        except Exception as e:
            # logger.info(f"error in making grpc call::url: {url}, |error: {e}")
            return 0

    def tearDown(self):
        self.repo.execute("DELETE FROM service")
        self.repo.execute("DELETE FROM service_endpoint")
