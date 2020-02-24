import unittest
from common.constant import StatusCode
from verification.utils import get_user_reference_id_from_username
from verification.application.services.user_verification_service import UserVerificationService, user_verification_repo
from unittest.mock import patch
from verification.infrastructure.models import UserVerificationModel
from verification.constants import UserVerificationStatus

user_verification_service = UserVerificationService()


class TestUserVerificationService(unittest.TestCase):
    @patch("requests.post")
    @patch("common.boto_utils.BotoUtils.get_ssm_parameter")
    def test_initiate(self, mock_ssm_parameter, mock_post_request):
        sample_response = {
            "timestamp": "2018-07-03T08:23:12.494Z",
            "transactionReference": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "redirectUrl": "https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx"
        }
        mock_ssm_parameter.return_value = "abcd"
        mock_post_request.return_value.status_code = StatusCode.OK
        mock_post_request.return_value.json.return_value = sample_response

        username = "peterparker@marvel.io"
        response = user_verification_service.initiate(username)
        if response == sample_response:
            user_verification_model = user_verification_repo.session.query(UserVerificationModel)\
                .filter(UserVerificationModel.user_reference_id == get_user_reference_id_from_username(username))\
                .filter(UserVerificationModel.verification_status == UserVerificationStatus.PENDING.value)\
                .first()
            if user_verification_model is None:
                assert False
            else:
                assert True
        else:
            assert False


if __name__ == '__main__':
    unittest.main()
