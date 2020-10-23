import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock
from uuid import uuid4

from common.exceptions import MethodNotImplemented
from verification.application.handlers.verification_handlers import initiate, callback
from verification.application.services.verification_manager import verification_repository
from verification.constants import VerificationStatus, DUNSVerificationStatus
from verification.infrastructure.models import VerificationModel


class TestIndividualVerification(TestCase):

    def test_initiate(self):
        username = "karl@dummy.io"
        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "body": json.dumps({
                "type": "INDIVIDUAL"
            })
        }
        initiate(event, None)
        verification = verification_repository.session.query(VerificationModel) \
            .filter(VerificationModel.entity_id == username) \
            .order_by(VerificationModel.created_at.desc()).first()
        if verification is None:
            assert False
        self.assertEqual(VerificationStatus.APPROVED.value, verification.status)
        self.assertEqual(username, verification.entity_id)

    @patch("common.boto_utils.BotoUtils", return_value=Mock(get_ssm_parameter=Mock(return_value="123"),
           invoke_lambda=Mock(return_value={"statusCode": 201})))
    def test_callback(self, mock_boto):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "INDIVIDUAL"
        org_uuid = uuid4().hex
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=org_uuid, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))

        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "queryStringParameters": {"verification_id": test_verification_id},
            "body": json.dumps({
                "verificationStatus": "APPROVED",
                "reviewed_by": "admin@dummy.io",
                "comment": "looks good"
            })
        }
        self.assertRaises(Exception, callback, event, None)

    def tearDown(self):
        verification_repository.session.query(VerificationModel).delete()
        verification_repository.session.commit()
