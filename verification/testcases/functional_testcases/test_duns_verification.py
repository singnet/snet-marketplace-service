import json
from datetime import datetime
from unittest import TestCase
from uuid import uuid4

from verification.application.handlers.verification_handlers import initiate, callback
from verification.application.services.verification_manager import verification_repository, duns_repository
from verification.constants import VerificationStatus, DUNSVerificationStatus
from verification.infrastructure.models import DUNSVerificationModel, VerificationModel


class TestDUNSVerification(TestCase):

    def test_initiate(self):
        username = "karl@dummy.io"
        org_uuid = uuid4().hex
        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "body": json.dumps({
                "type": "DUNS",
                "entity_id": org_uuid
            })
        }
        response = initiate(event, None)
        verification = verification_repository.session.query(VerificationModel) \
            .filter(VerificationModel.entity_id == org_uuid) \
            .order_by(VerificationModel.created_at.desc()).first()
        if verification is None:
            assert False
        self.assertEqual(VerificationStatus.PENDING.value, verification.status)
        verification_id = verification.id

        duns_verification = duns_repository.session.query(DUNSVerificationModel) \
            .filter(DUNSVerificationModel.verification_id == verification_id).first()
        if duns_verification is None:
            assert False
        self.assertEqual(DUNSVerificationStatus.PENDING.value, duns_verification.status)
        self.assertEqual(org_uuid, duns_verification.org_uuid)

    def test_callback(self):
        test_verification_id = "9f2c90119cb7424b8d69319ce211ddfc"
        verification_type = "DUNS"
        org_uuid = uuid4().hex
        username = "karl@dummy.io"
        current_time = datetime.utcnow()
        verification_repository.add_item(VerificationModel(
            id=test_verification_id, verification_type=verification_type, entity_id=org_uuid, status="PENDING",
            requestee=username, created_at=current_time, updated_at=current_time
        ))

        duns_repository.add_item(DUNSVerificationModel(
            verification_id=test_verification_id, org_uuid=org_uuid, comments=[],
            status=DUNSVerificationStatus.PENDING.value, created_at=current_time, updated_at=current_time))

        event = {
            "requestContext": {"authorizer": {"claims": {"email": username}}},
            "pathParameters": {"verification_id": test_verification_id},
            "body": json.dumps({
                "verificationStatus": "APPROVED",
                "username": "admin@dummy.io",
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
        duns_verification = duns_repository.session.query(DUNSVerificationModel) \
            .filter(DUNSVerificationModel.verification_id == test_verification_id).first()
        if duns_verification is None:
            assert False
        self.assertEqual(DUNSVerificationStatus.APPROVED.value, duns_verification.status)
        self.assertEqual(org_uuid, duns_verification.org_uuid)
        self.assertEqual(1, len(duns_verification.comments))

    def tearDown(self):
        duns_repository.session.query(DUNSVerificationModel).delete()
        verification_repository.session.query(VerificationModel).delete()
        verification_repository.session.commit()
