from verification.domain.models.jumio import JumioVerification
from verification.domain.models.verfication import Verification


class VerificationFactory:

    @staticmethod
    def verification_entity_from_db_list(verification_db_list):
        verifications = []
        for verification_db in verification_db_list:
            verifications.append(VerificationFactory.verification_entity_from_db(verification_db))
        return verifications

    @staticmethod
    def verification_entity_from_db(verification_db):
        return Verification(
            verification_db.id, verification_db.verification_type, verification_db.entity_id,
            verification_db.status, verification_db.requestee, verification_db.created_at, verification_db.updated_at)

    @staticmethod
    def jumio_verification_entity_from_db_list(verification_db_list):
        verifications = []
        for verification_db in verification_db_list:
            verifications.append(VerificationFactory.jumio_verification_entity_from_db(verification_db))
        return verifications

    @staticmethod
    def jumio_verification_entity_from_db(verification_db):
        return JumioVerification(
            verification_id=verification_db.verification_id, username=verification_db.username,
            user_reference_id=verification_db.user_reference_id, verification_status=verification_db.verification_status,
            transaction_status=verification_db.transaction_status, created_at=verification_db.created_at,
            redirect_url=verification_db.redirect_url, jumio_reference_id=verification_db.jumio_reference_id,
            transaction_date=verification_db.transaction_date, callback_date=verification_db.callback_date
        )
