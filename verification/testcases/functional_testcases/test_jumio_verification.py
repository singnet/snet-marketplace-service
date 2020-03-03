import json
from _sha1 import sha1
from unittest import TestCase
from unittest.mock import patch, Mock

from verification.application.handlers.verification_handlers import initiate
from verification.application.services.verification_manager import verification_repository, jumio_repository
from verification.constants import JumioTransactionStatus, VerificationStatus
from verification.infrastructure.models import JumioVerificationModel, VerificationModel
from verification.testcases.test_veriables import test_initiate_redirect_url


class TestJumioVerification(TestCase):

    def setUp(self):
        pass

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    @patch("requests.post", return_value=Mock(
        json=Mock(return_value={
            "timestamp": "2018-07-03T08:23:12.494Z", "transactionReference": "123-13-13-134-1234",
            "redirectUrl": test_initiate_redirect_url
        }),
        status_code=200
    ))
    def test_jumio_initiate(self, mock_requests_post, mock_boto_utils):
        username = "karl@dummy.io"
        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "body": json.dumps({
                "type": "JUMIO",
                "entity_id": username
            })
        }
        response = initiate(event, None)
        self.assertDictEqual(response, {
            'statusCode': 201,
            'body': '{"status": "success", "data": {"redirect_url": '
                    '"https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx"}}',
            'headers': {
                'Content-Type': 'application/json', 'X-Requested-With': '*',
                'Access-Control-Allow-Headers':
                    'Access-Control-Allow-Origin, Content-Type, X-Amz-Date, Authorization,X-Api-Key,x-requested-with',
                'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET,OPTIONS,POST'}})
        jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
        if jumio_verfication is None:
            assert False
        self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
        self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
        self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.PENDING.value)
        self.assertEqual(jumio_verfication.username, username)
        self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())

        verification = verification_repository.session.query(VerificationModel).first()
        if verification is None:
            assert False
        self.assertEqual(verification.entity_id, username)
        self.assertEqual(verification.status, VerificationStatus.PENDING.value)
        self.assertEqual(verification.requestee, username)
        self.assertEqual(verification.verification_type, "JUMIO")
        assert verification.id is not None or verification.id != ""

    def tearDown(self):
        jumio_repository.session.query(JumioVerificationModel).delete()
        verification_repository.session.query(VerificationModel).delete()
        jumio_repository.session.commit()
