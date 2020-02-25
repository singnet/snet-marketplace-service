import unittest
from common.constant import StatusCode
from verification.utils import get_user_reference_id_from_username
from verification.application.services.user_verification_service import UserVerificationService, user_verification_repo
from unittest.mock import patch
from verification.infrastructure.models import UserVerificationModel
from verification.constants import UserVerificationStatus
import datetime

user_verification_service = UserVerificationService()


class TestUserVerificationService(unittest.TestCase):
    def setUp(self):
        self.username = "peterparker@marvel.io"
        self.transaction_id = "4fe04f985eab4b40ac06545393c0ef55"
        self.jumio_reference = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"


    @patch("uuid.uuid4")
    @patch("requests.post")
    @patch("common.boto_utils.BotoUtils.get_ssm_parameter")
    def test_initiate(self, mock_ssm_parameter, mock_post_request, mock_uuid4):
        mock_uuid4.return_value.hex = self.transaction_id
        sample_response = {
            "timestamp": "2018-07-03T08:23:12.494Z",
            "transactionReference": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "redirectUrl": "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx"
        }
        mock_ssm_parameter.return_value = "abcd"
        mock_post_request.return_value.status_code = StatusCode.OK
        mock_post_request.return_value.json.return_value = sample_response

        response = user_verification_service.initiate(self.username)
        if response == sample_response:
            user_verification_model = user_verification_repo.session.query(UserVerificationModel) \
                .filter(UserVerificationModel.jumio_reference == sample_response["transactionReference"]) \
                .filter(UserVerificationModel.verification_status == UserVerificationStatus.PENDING.value) \
                .first()
            if user_verification_model is None:
                assert False
            else:
                assert True
        else:
            assert False

    def test_submit_success(self):
        user_verification_repo \
            .session.add(UserVerificationModel(transaction_id=self.transaction_id,
                                               user_reference_id=get_user_reference_id_from_username(
                                                   self.username),
                                               jumio_reference=self.jumio_reference,
                                               verification_status=UserVerificationStatus.PENDING.value))
        response = user_verification_service.submit(self.transaction_id, None)
        if response == "OK":
            user_verification_model = user_verification_repo.session.query(UserVerificationModel) \
                .filter(UserVerificationModel.transaction_id == self.transaction_id) \
                .first()
            if user_verification_model.verification_status == UserVerificationStatus.SUBMIT_SUCCESS.value:
                assert True
            else:
                assert False
        else:
            assert False

    def test_submit_error(self):
        user_verification_repo \
            .session.add(UserVerificationModel(transaction_id=self.transaction_id,
                                               user_reference_id=get_user_reference_id_from_username(
                                                   self.username),
                                               jumio_reference=self.jumio_reference,
                                               verification_status=UserVerificationStatus.PENDING.value))
        error_code = 9100
        response = user_verification_service.submit(self.transaction_id, error_code)
        if response == "OK":
            user_verification_model = user_verification_repo.session.query(UserVerificationModel) \
                .filter(UserVerificationModel.transaction_id == self.transaction_id) \
                .first()
            if user_verification_model.verification_status == UserVerificationStatus.SUBMIT_ERROR.value:
                assert True
            else:
                assert False
        else:
            assert False

    def test_complete(self):
        user_verification_repo \
            .session.add(UserVerificationModel(transaction_id=self.transaction_id,
                                               user_reference_id=get_user_reference_id_from_username(
                                                   self.username),
                                               jumio_reference=self.jumio_reference,
                                               verification_status=UserVerificationStatus.PENDING.value))
        payload = {
            "jumioIdScanReference": self.jumio_reference,
            "callBackType": "NETVERIFYID",
            "verificationStatus": "APPROVED_VERIFIED",
            "idScanStatus": "SUCCESS",
            "idScanSource": "WEB",
            "transactionDate": datetime.datetime.now(),
            "callbackDate": datetime.datetime.now(),
            "identityVerification": "{}",
            "idType": "PASSPORT",
        }
        response = user_verification_service.complete(payload)
        if response == "OK":
            user_verification_model = user_verification_repo.session.query(UserVerificationModel) \
                .filter(UserVerificationModel.jumio_reference == payload["jumioIdScanReference"]) \
                .first()
            verification_approved = user_verification_model.verification_status == UserVerificationStatus.\
                APPROVED_VERIFIED.value
            verification_denied = user_verification_model.verification_status == UserVerificationStatus.\
                DENIED_FRAUD.value
            if verification_approved or verification_denied:
                assert True
            else:
                assert False
        else:
            assert False

    def tearDown(self):
        user_verification_repo.session.query(UserVerificationModel).delete()

if __name__ == '__main__':
    unittest.main()
