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
        Verification(
            verification_db.id, verification_db.verfication_type, verification_db.entity_id,
            verification_db.status, verification_db.requestee, verification_db.created_at, verification_db.updated_at)
