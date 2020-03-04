import json
from _sha1 import sha1
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock

from verification.application.handlers.jumio_verification_handlers import submit
from verification.application.handlers.verification_handlers import initiate, get_status, callback
from verification.application.services.verification_manager import verification_repository, jumio_repository
from verification.constants import JumioTransactionStatus, VerificationStatus, JumioVerificationStatus, \
    REJECTED_JUMIO_VERIFICATION
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

        verification = verification_repository.session.query(VerificationModel).first()
        if verification is None:
            assert False
        self.assertEqual(verification.entity_id, username)
        self.assertEqual(verification.status, VerificationStatus.PENDING.value)
        self.assertEqual(verification.requestee, username)
        self.assertEqual(verification.verification_type, "JUMIO")
        assert verification.id is not None or verification.id != ""

        jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
        if jumio_verfication is None:
            assert False
        self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
        self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
        self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.PENDING.value)
        self.assertEqual(jumio_verfication.username, username)
        self.assertEqual(jumio_verfication.verification_status, JumioVerificationStatus.PENDING.value)
        self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_jumio_submit_with_success(self, mock_boto_utils):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "JUMIO"
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=username, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))
        jumio_repository.add_item(JumioVerificationModel(
            verification_id=test_verification_id, username=username, jumio_reference_id="123-13-13-134-1234",
            user_reference_id=sha1(username.encode("utf-8")).hexdigest(),
            redirect_url="https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx",
            transaction_status="PENDING", verification_status="PENDING", transaction_date=current_time,
            created_at=current_time
        ))
        event = {
            "queryStringParameters": {
                "transactionStatus": "SUCCESS"
            },
            "pathParameters": {
                "verification_id": test_verification_id
            }
        }
        submit(event, None)
        verification = verification_repository.session.query(VerificationModel).first()
        if verification is None:
            assert False
        self.assertEqual(verification.entity_id, username)
        self.assertEqual(verification.status, VerificationStatus.PENDING.value)
        self.assertEqual(verification.requestee, username)
        self.assertEqual(verification.verification_type, "JUMIO")
        assert (verification.id is not None or verification.id != "") and verification.id == test_verification_id

        jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
        if jumio_verfication is None:
            assert False
        self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
        self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
        self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.SUCCESS.value)
        self.assertEqual(jumio_verfication.verification_status, JumioVerificationStatus.PENDING.value)
        self.assertEqual(jumio_verfication.username, username)
        self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_jumio_submit_with_error(self, mock_boto_utils):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "JUMIO"
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=username, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))
        jumio_repository.add_item(JumioVerificationModel(
            verification_id=test_verification_id, username=username, jumio_reference_id="123-13-13-134-1234",
            user_reference_id=sha1(username.encode("utf-8")).hexdigest(),
            redirect_url="https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx",
            transaction_status="PENDING", verification_status="PENDING", transaction_date=current_time,
            created_at=current_time
        ))
        event = {
            "queryStringParameters": {
                "transactionStatus": "ERROR"
            },
            "pathParameters": {
                "verification_id": test_verification_id
            }
        }
        submit(event, None)
        verification = verification_repository.session.query(VerificationModel).first()
        if verification is None:
            assert False
        self.assertEqual(verification.entity_id, username)
        self.assertEqual(verification.status, VerificationStatus.ERROR.value)
        self.assertEqual(verification.requestee, username)
        self.assertEqual(verification.verification_type, "JUMIO")
        assert (verification.id is not None or verification.id != "") and verification.id == test_verification_id

        jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
        if jumio_verfication is None:
            assert False
        self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
        self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
        self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.ERROR.value)
        self.assertEqual(jumio_verfication.verification_status, JumioVerificationStatus.PENDING.value)
        self.assertEqual(jumio_verfication.username, username)
        self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_jumio_get_status(self, mock_boto_utils):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "JUMIO"
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=username, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))
        jumio_repository.add_item(JumioVerificationModel(
            verification_id=test_verification_id, username=username, jumio_reference_id="123-13-13-134-1234",
            user_reference_id=sha1(username.encode("utf-8")).hexdigest(),
            redirect_url="https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx",
            transaction_status="PENDING", verification_status="PENDING", transaction_date=current_time,
            created_at=current_time
        ))
        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "queryStringParameters": {
                "type": "JUMIO"
            }
        }
        verification = json.loads(get_status(event, None)["body"])["data"]
        self.assertEqual(verification["entity_id"], username)
        self.assertEqual(verification["status"], VerificationStatus.PENDING.value)
        self.assertEqual(verification["requestee"], username)
        self.assertEqual(verification["type"], "JUMIO")
        assert (verification["id"] is not None or verification["id"] != "") and verification[
            "id"] == test_verification_id

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_jumio_callback_approved(self, mock_boto_utils):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "JUMIO"
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=username, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))
        jumio_repository.add_item(JumioVerificationModel(
            verification_id=test_verification_id, username=username, jumio_reference_id="123-13-13-134-1234",
            user_reference_id=sha1(username.encode("utf-8")).hexdigest(),
            redirect_url="https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx",
            transaction_status=JumioTransactionStatus.SUCCESS.value,
            verification_status=JumioVerificationStatus.PENDING.value, transaction_date=current_time,
            created_at=current_time
        ))
        event = {
            "body": json.dumps({
                "verificationStatus": JumioVerificationStatus.APPROVED_VERIFIED.value,
                "callbackDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }),
            "pathParameters": {
                "verification_id": test_verification_id
            }
        }
        callback(event, None)
        verification = verification_repository.session.query(VerificationModel).first()
        if verification is None:
            assert False
        self.assertEqual(verification.entity_id, username)
        self.assertEqual(verification.status, VerificationStatus.APPROVED.value)
        self.assertEqual(verification.requestee, username)
        self.assertEqual(verification.verification_type, "JUMIO")
        assert (verification.id is not None or verification.id != "") and verification.id == test_verification_id

        jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
        if jumio_verfication is None:
            assert False
        self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
        self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
        self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.DONE.value)
        self.assertEqual(jumio_verfication.verification_status, JumioVerificationStatus.APPROVED_VERIFIED.value)
        self.assertEqual(jumio_verfication.username, username)
        self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_jumio_callback_rejected(self, mock_boto_utils):
        for status in REJECTED_JUMIO_VERIFICATION:
            test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
            verification_type = "JUMIO"
            username = "karl@dummy.io"
            current_time = datetime.utcnow()
            verification_repository.add_item(VerificationModel(
                id=test_verification_id, verification_type=verification_type, entity_id=username, status="PENDING",
                requestee=username, created_at=current_time, updated_at=current_time
            ))
            jumio_repository.add_item(JumioVerificationModel(
                verification_id=test_verification_id, username=username, jumio_reference_id="123-13-13-134-1234",
                user_reference_id=sha1(username.encode("utf-8")).hexdigest(),
                redirect_url="https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx",
                transaction_status=JumioTransactionStatus.SUCCESS.value,
                verification_status=JumioVerificationStatus.PENDING.value, transaction_date=current_time,
                created_at=current_time
            ))
            event = {
                "body": json.dumps({
                    "verificationStatus": status,
                    "callbackDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }),
                "pathParameters": {
                    "verification_id": test_verification_id
                }
            }
            callback(event, None)
            verification = verification_repository.session.query(VerificationModel).first()
            if verification is None:
                assert False
            self.assertEqual(verification.entity_id, username)
            self.assertEqual(verification.status, VerificationStatus.REJECTED.value)
            self.assertEqual(verification.requestee, username)
            self.assertEqual(verification.verification_type, "JUMIO")
            assert (verification.id is not None or verification.id != "") and verification.id == test_verification_id

            jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
            if jumio_verfication is None:
                assert False
            self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
            self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
            self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.DONE.value)
            self.assertEqual(jumio_verfication.verification_status, status)
            self.assertEqual(jumio_verfication.username, username)
            self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())
            self.tearDown()

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_jumio_callback_failed_one(self, mock_boto_utils):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "JUMIO"
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=username, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))
        jumio_repository.add_item(JumioVerificationModel(
            verification_id=test_verification_id, username=username, jumio_reference_id="123-13-13-134-1234",
            user_reference_id=sha1(username.encode("utf-8")).hexdigest(),
            redirect_url="https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx",
            transaction_status=JumioTransactionStatus.SUCCESS.value,
            verification_status=JumioVerificationStatus.PENDING.value, transaction_date=current_time,
            created_at=current_time
        ))
        event = {
            "body": json.dumps({
                "verificationStatus": JumioVerificationStatus.ERROR_NOT_READABLE_ID.value,
                "callbackDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }),
            "pathParameters": {
                "verification_id": test_verification_id
            }
        }
        callback(event, None)
        verification = verification_repository.session.query(VerificationModel).first()
        if verification is None:
            assert False
        self.assertEqual(verification.entity_id, username)
        self.assertEqual(verification.status, VerificationStatus.FAILED.value)
        self.assertEqual(verification.requestee, username)
        self.assertEqual(verification.verification_type, "JUMIO")
        assert (verification.id is not None or verification.id != "") and verification.id == test_verification_id

        jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
        if jumio_verfication is None:
            assert False
        self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
        self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
        self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.DONE.value)
        self.assertEqual(jumio_verfication.verification_status, JumioVerificationStatus.ERROR_NOT_READABLE_ID.value)
        self.assertEqual(jumio_verfication.username, username)
        self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123")))
    def test_jumio_callback_failed_two(self, mock_boto_utils):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "JUMIO"
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=username, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))
        jumio_repository.add_item(JumioVerificationModel(
            verification_id=test_verification_id, username=username, jumio_reference_id="123-13-13-134-1234",
            user_reference_id=sha1(username.encode("utf-8")).hexdigest(),
            redirect_url="https://yourcompany.netverify.com/web/v4/app?locale=en-GB&authorizationToken=xxx",
            transaction_status=JumioTransactionStatus.SUCCESS.value,
            verification_status=JumioVerificationStatus.PENDING.value, transaction_date=current_time,
            created_at=current_time
        ))
        event = {
            "body": json.dumps({
                "verificationStatus": JumioVerificationStatus.NO_ID_UPLOADED.value,
                "callbackDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }),
            "pathParameters": {
                "verification_id": test_verification_id
            }
        }
        callback(event, None)
        verification = verification_repository.session.query(VerificationModel).first()
        if verification is None:
            assert False
        self.assertEqual(verification.entity_id, username)
        self.assertEqual(verification.status, VerificationStatus.FAILED.value)
        self.assertEqual(verification.requestee, username)
        self.assertEqual(verification.verification_type, "JUMIO")
        assert (verification.id is not None or verification.id != "") and verification.id == test_verification_id

        jumio_verfication = jumio_repository.session.query(JumioVerificationModel).first()
        if jumio_verfication is None:
            assert False
        self.assertEqual(jumio_verfication.jumio_reference_id, '123-13-13-134-1234')
        self.assertEqual(jumio_verfication.redirect_url, test_initiate_redirect_url)
        self.assertEqual(jumio_verfication.transaction_status, JumioTransactionStatus.FAILED.value)
        self.assertEqual(jumio_verfication.verification_status, JumioVerificationStatus.NO_ID_UPLOADED.value)
        self.assertEqual(jumio_verfication.username, username)
        self.assertEqual(jumio_verfication.user_reference_id, sha1(username.encode("utf-8")).hexdigest())


    def tearDown(self):
        jumio_repository.session.query(JumioVerificationModel).delete()
        verification_repository.session.query(VerificationModel).delete()
        jumio_repository.session.commit()
