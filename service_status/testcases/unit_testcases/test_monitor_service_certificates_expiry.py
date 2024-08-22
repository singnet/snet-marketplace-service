import unittest
from unittest import TestCase
from datetime import datetime as dt
from datetime import timedelta
from service_status.monitor_service import MonitorServiceCertificate, MonitorService
from common.repository import Repository
from service_status.config import NETWORK_ID, NETWORKS
from unittest.mock import patch

NETWORK_NAME = NETWORKS[NETWORK_ID]["name"]


class TestMonitorServiceCertificatesExpiry(TestCase):
    def setUp(self):
        self.monitor_service_certificate = MonitorServiceCertificate(
            repo=Repository(net_id=NETWORK_ID, NETWORKS=NETWORKS))

    def test_get_certificate_expiration_slack_notification_message(self):
        org_id = "test_org_id"
        service_id = "test_service_id"
        endpoint = "https://dummyendpoint.com"
        days_left_for_expiration = 10
        response = self.monitor_service_certificate._get_certificate_expiration_slack_notification_message(
            org_id=org_id, service_id=service_id, endpoint=endpoint, days_left_for_expiration=days_left_for_expiration)
        assert (response == "Certificates for service test_service_id under organization test_org_id for "
                            "the TEST network are about to expire in 10 days.")

    def test_get_certificate_expiration_email_notification_message(self):
        org_id = "test_org_id"
        service_id = "test_service_id"
        endpoint = "https://dummyendpoint.com"
        days_left_for_expiration = 10
        response = self.monitor_service_certificate._get_certificate_expiration_email_notification_message(
            org_id=org_id, service_id=service_id, endpoint=endpoint, days_left_for_expiration=days_left_for_expiration)
        assert (
                response == "<html><head></head><body><div><p>Hello,</p><p>Your certificates for service test_service_id "
                            "under organization test_org_id for the TEST network are about to expire in 10 days. Please "
                            "take immediate action to renew them.</p><p>Endpoint: https://dummyendpoint.com</p><br /> "
                            "<br /><p><em>Please do not reply to the email for any enquiries for any queries please email"
                            " at cs-marketplace@singularitynet.io.</em></p><p>Warmest regards, <br />SingularityNET "
                            "Marketplace Team</p></div></body></html>")

    def test_get_certificate_expiration_email_notification_subject(self):
        org_id = "test_org_id"
        service_id = "test_service_id"
        endpoint = "https://dummyendpoint.com"
        response = self.monitor_service_certificate._get_certificate_expiration_email_notification_subject(
            org_id=org_id, service_id=service_id, endpoint=endpoint)
        assert (response == "Certificates are about to expire for service test_service_id for TEST network.")

    def test_is_valid_url(self):
        endpoint = "https://dummy.com:0000"
        response = MonitorServiceCertificate(repo=None)._valid_url(url=endpoint)
        assert (response == True)
        endpoint = "127.0.0.1:9999"
        response = MonitorServiceCertificate(repo=None)._valid_url(url=endpoint)
        assert (response == False)
