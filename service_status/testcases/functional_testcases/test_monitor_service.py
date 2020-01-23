import unittest
from unittest import TestCase
from datetime import datetime as dt
from datetime import timedelta
from service_status.handlers.monitor_service_handlers import monitor_service_certificates_expiry_handler
from common.repository import Repository
from service_status.config import NETWORK_ID, NETWORKS
from unittest.mock import patch


class TestMonitorService(TestCase):
    def setUp(self):
        pass

    @patch("service_status.monitor_service.MonitorServiceCertificate._get_service_endpoint_data")
    @patch(
        "service_status.monitor_service.MonitorServiceCertificate._get_certification_expiration_date_for_given_service")
    @patch("service_status.monitor_service.MonitorServiceCertificate._get_service_provider_email")
    @patch("common.utils.Utils.report_slack")
    @patch("service_status.monitor_service.MonitorServiceCertificate._send_email_notification")
    def test_monitor_service_certificate_expiry_handler(
            self, _send_email_notification, report_slack, _get_service_provider_email, _get_certification_expiration_date_for_given_service,
            _get_service_endpoint_data):
        _get_service_endpoint_data.return_value = [
            {"endpoint": "https://dummy.com:9999", "org_id": "test_org_id", "service_id": "test_service"}]
        _get_certification_expiration_date_for_given_service.return_value = dt.utcnow() + timedelta(days=25)
        _get_service_provider_email.return_value = ["prashant@singularitynet.io"]
        report_slack.return_value = None
        _send_email_notification.return_value = None
        response = monitor_service_certificates_expiry_handler(event={}, context=None)
        assert (response == "success")
