from unittest import TestCase
from unittest.mock import patch, Mock

from verification.application.services.verification_manager import VerificationManager


class TestVerificationManager(TestCase):

    @patch("verification.application.services.verification_manager.verification_repository",
           return_value=Mock(add_verification=Mock(), get_all_verification=Mock(return_value=[])))
    @patch("verification.application.services.verification_manager.jumio_repository",
           return_value=Mock(add_jumio_verification=Mock()))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    @patch("requests.post", return_value=Mock(
        json=Mock(return_value={
            "timestamp": "2018-07-03T08:23:12.494Z", "transactionReference": "123-13-13-134-1234",
            "redirectUrl": "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx"
        }),
        status_code=200
    ))
    def test_initiate_verification_with_jumio(self, mock_requests_post, mock_boto_utils, mock_jumio_repo, mock_verification_repo):
        username = "karl@dummy.io"
        verification_details = {
            "type": "JUMIO",
            "entity_id": username
        }
        response = VerificationManager().initiate_verification(verification_details, username)
        self.assertEqual(response["redirect_url"], "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx")
