from verification.domain.factory.verification_factory import VerificationFactory
from verification.infrastructure.models import JumioVerificationModel
from verification.infrastructure.repositories.base_repository import BaseRepository


class JumioRepository(BaseRepository):

    def add_jumio_verification(self, verification):
        self.add_item(JumioVerificationModel(
            verification_id=verification.verification_id, username=verification.username,
            jumio_reference_id=verification.jumio_reference_id, user_reference_id=verification.user_reference_id,
            redirect_url=verification.redirect_url, transaction_status=verification.transaction_status,
            verification_status=verification.verification_status, reject_reason=verification.reject_reason,
            transaction_date=verification.transaction_date, callback_date=verification.callback_date,
            created_at=verification.created_at
        ))

    def _get_verification(self, verification_id):
        verification_db = self.session.query(JumioVerificationModel) \
            .filter(JumioVerificationModel.verification_id == verification_id).first()
        if verification_db is None:
            raise Exception("no data found")
        return verification_db

    def get_verification(self, verification_id):
        try:
            verification_db = self._get_verification(verification_id)
            verification = VerificationFactory.jumio_verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.session.close()
        return verification

    def update_transaction_status(self, verification_id, status):
        try:
            verification_db = self._get_verification(verification_id)
            verification_db.transaction_status = status
            verification = VerificationFactory.jumio_verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.session.close()
        return verification

    def update_verification_and_transaction_status(self, verification):
        try:
            verification_db = self._get_verification(verification.verification_id)
            verification_db.transaction_status = verification.transaction_status
            verification_db.verification_status = verification.verification_status
            verification_db.callback_date = verification.callback_date
            verification_db.reject_reason = verification.reject_reason
            verification = VerificationFactory.jumio_verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.session.close()
        return verification
