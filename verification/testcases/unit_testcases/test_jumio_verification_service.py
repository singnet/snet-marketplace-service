import unittest
from unittest.mock import patch, Mock

import requests

from verification.domain.services.jumio_service import JumioService


class TestJumioService(unittest.TestCase):

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    @patch("requests.post", return_value=Mock(
        json=Mock(return_value={
            "timestamp": "2018-07-03T08:23:12.494Z", "transactionReference": "123-13-13-134-1234",
            "redirectUrl": "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx"
        }),
        status_code=200
    ))
    def test_initiate(self, mock_requests_post, mock_boto_utils):
        mock_requests_post = requests.Response()
        jumio_verification = JumioService(Mock()).initiate("user", "karl@dummy.io")
        self.assertEqual(jumio_verification.redirect_url,
                         "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx")
        self.assertEqual(jumio_verification.jumio_reference_id, "123-13-13-134-1234")

