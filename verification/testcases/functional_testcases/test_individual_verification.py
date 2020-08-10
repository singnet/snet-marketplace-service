import json
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, Mock
from uuid import uuid4

from verification.application.handlers.verification_handlers import initiate, callback
from verification.application.services.verification_manager import verification_repository, individual_repository
from verification.constants import VerificationStatus, DUNSVerificationStatus
from verification.infrastructure.models import IndividualVerificationModel, VerificationModel


class TestIndividualVerification(TestCase):

    def test_initiate(self):
        username = "karl@dummy.io"
        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "body": json.dumps({
                "type": "INDIVIDUAL"
            })
        }
        response = initiate(event, None)
        verification = verification_repository.session.query(VerificationModel) \
            .filter(VerificationModel.entity_id == username) \
            .order_by(VerificationModel.created_at.desc()).first()
        if verification is None:
            assert False
        self.assertEqual(VerificationStatus.PENDING.value, verification.status)
        verification_id = verification.id

        individual_verification = individual_repository.session.query(IndividualVerificationModel) \
            .filter(IndividualVerificationModel.verification_id == verification_id).first()
        if individual_verification is None:
            assert False
        self.assertEqual(DUNSVerificationStatus.PENDING.value, individual_verification.status)
        self.assertEqual(username, individual_verification.username)

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

        individual_repository.add_item(IndividualVerificationModel(
            verification_id=test_verification_id, username=username, comments=[],
            status=DUNSVerificationStatus.PENDING.value, created_at=current_time, updated_at=current_time))

        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "queryStringParameters": {"verification_id": test_verification_id},
            "body": json.dumps({
                "verificationStatus": "APPROVED",
                "reviewed_by": "admin@dummy.io",
                "comment": "looks good"
            })
        }
        callback(event, None)
        verification = verification_repository.session.query(VerificationModel) \
            .filter(VerificationModel.entity_id == org_uuid) \
            .order_by(VerificationModel.created_at.desc()).first()
        if verification is None:
            assert False
        self.assertEqual(VerificationStatus.APPROVED.value, verification.status)
        duns_verification = individual_repository.session.query(IndividualVerificationModel) \
            .filter(IndividualVerificationModel.verification_id == test_verification_id).first()
        if duns_verification is None:
            assert False
        self.assertEqual(DUNSVerificationStatus.APPROVED.value, duns_verification.status)
        self.assertEqual(username, duns_verification.username)
        self.assertEqual(1, len(duns_verification.comments))

    def tearDown(self):
        individual_repository.session.query(IndividualVerificationModel).delete()
        verification_repository.session.query(VerificationModel).delete()
        verification_repository.session.commit()
