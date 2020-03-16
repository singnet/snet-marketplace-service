from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock
from uuid import uuid4

from verification.application.services.verification_manager import VerificationManager
from verification.config import DAPP_POST_JUMIO_URL
from verification.constants import JumioVerificationStatus, VerificationStatus, JumioTransactionStatus
from verification.domain.models.jumio import JumioVerification
from verification.domain.models.verfication import Verification


class TestVerificationManager(TestCase):

    @patch("verification.application.services.verification_manager.verification_repository",
           return_value=Mock(add_verification=Mock(), get_all_verification=Mock(return_value=[])))
    @patch("verification.application.services.verification_manager.jumio_repository",
           return_value=Mock(add_jumio_verification=Mock()))
    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123"),
           invoke_lambda=Mock(return_value={"statusCode": 201})))
    @patch("requests.post", return_value=Mock(
        json=Mock(return_value={
            "timestamp": "2018-07-03T08:23:12.494Z", "transactionReference": "123-13-13-134-1234",
            "redirectUrl": "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx"
        }),
        status_code=200
    ))
    def test_initiate_verification_with_allowed_domain_users(self, mock_requests_post, mock_boto_utils, mock_jumio_repo,
                                                             mock_verification_repo):
        username = "karl@allowed.io"
        verification_details = {
            "type": "JUMIO",
            "entity_id": username
        }
        response = VerificationManager().initiate_verification(verification_details, username)
        self.assertEqual(response["redirect_url"],
                         "")

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
    def test_initiate_verification_with_jumio(self, mock_requests_post, mock_boto_utils, mock_jumio_repo,
                                              mock_verification_repo):
        username = "karl@dummy.io"
        verification_details = {
            "type": "JUMIO",
            "entity_id": username
        }
        response = VerificationManager().initiate_verification(verification_details, username)
        self.assertEqual(response["redirect_url"],
                         "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx")

    @patch("verification.application.services.verification_manager.verification_repository")
    @patch("verification.application.services.verification_manager.jumio_repository")
    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_submit(self, mock_boto_utils, mock_jumio_repo, mock_verification_repo):
        verification_id = uuid4().hex
        username = "karl@snet.io"
        user_reference_id = "6a7e9b7d8a9e61566a7bd24345cbebdbea08389f"
        created_at = datetime.utcnow()

        mock_verification = Verification(id=verification_id, type="JUMIO", entity_id=username,
                                         status=VerificationStatus.PENDING.value, requestee=username,
                                         created_at=created_at, updated_at=created_at)
        mock_verification_repo.get_verification = Mock(return_value=mock_verification)
        mock_verification_repo.update_status = Mock()
        mock_jumio_verification = JumioVerification(
            verification_id=verification_id, username=username, user_reference_id=user_reference_id,
            created_at=created_at, redirect_url="url", verification_status=JumioVerificationStatus.PENDING.value,
            transaction_status=JumioTransactionStatus.PENDING.value)
        mock_jumio_repo.update_transaction_status = Mock(return_value=mock_jumio_verification)

        response = VerificationManager().submit(verification_id, "SUCCESS")
        self.assertEqual(response, DAPP_POST_JUMIO_URL)

    @patch("verification.application.services.verification_manager.verification_repository")
    @patch("verification.application.services.verification_manager.jumio_repository")
    @patch("common.boto_utils.BotoUtils", return_value=Mock(
        get_ssm_parameter=Mock(return_value="123")))
    def test_callback(self, mock_boto_utils, mock_jumio_repo, mock_verification_repo):
        verification_id = uuid4().hex
        username = "karl@snet.io"
        user_reference_id = "6a7e9b7d8a9e61566a7bd24345cbebdbea08389f"
        created_at = datetime.utcnow()

        mock_verification = Verification(id=verification_id, type="JUMIO", entity_id=username,
                                         status=VerificationStatus.PENDING.value, requestee=username,
                                         created_at=created_at, updated_at=created_at)
        mock_verification_repo.get_verification = Mock(return_value=mock_verification)
        mock_verification_repo.update_status = Mock()
        mock_jumio_verification = JumioVerification(
            verification_id=verification_id, username=username, user_reference_id=user_reference_id,
            created_at=created_at, redirect_url="url",
            verification_status=JumioVerificationStatus.APPROVED_VERIFIED.value,
            transaction_status=JumioTransactionStatus.DONE.value)
        mock_jumio_repo.update_verification_and_transaction_status = Mock(return_value=mock_jumio_verification)

        payload = {
            "callbackDate": "2001-05-02T20:23:10.123Z",
            "verificationStatus": "APPROVED_VERIFIED"
        }
