from verification.domain.models.comment import Comment
from verification.domain.models.duns_verification import DUNSVerification
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
            verification_db.status, verification_db.requestee, verification_db.created_at, verification_db.updated_at,
            reject_reason=verification_db.reject_reason
        )

    @staticmethod
    def duns_verification_entity_from_db(verification_db):
        return DUNSVerification(
            verification_id=verification_db.verification_id, org_uuid=verification_db.org_uuid,
            status=verification_db.status,
            comments=VerificationFactory.comment_entity_list_from_json(verification_db.comments),
            created_at=verification_db.created_at,
            updated_at=verification_db.updated_at
        )

    @staticmethod
    def comment_entity_list_from_json(comments_json):
        return [Comment(comment=comment["comment"], created_by=comment["created_by"],
                        created_at=comment["created_at"])
                for comment in comments_json]
