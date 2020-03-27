from datetime import datetime

from verification.domain.factory.verification_factory import VerificationFactory
from verification.infrastructure.models import VerificationModel
from verification.infrastructure.repositories.base_repository import BaseRepository


class VerificationRepository(BaseRepository):

    def get_all_verification(self, entity_id, verification_type):
        try:
            verification_db_list = self.session.query(VerificationModel) \
                .filter(VerificationModel.entity_id == entity_id) \
                .filter(VerificationModel.verification_type == verification_type).all()
            verifications = VerificationFactory.verification_entity_from_db_list(verification_db_list)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.session.close()
        return verifications

    def _get_verification(self, verification_id):
        verification_db = self.session.query(VerificationModel) \
                .filter(VerificationModel.id == verification_id).first()
        if verification_db is None:
            raise Exception("no data found")
        return verification_db

    def add_verification(self, verification):
        self.add_item(VerificationModel(
            id=verification.id, verification_type=verification.type, entity_id=verification.entity_id,
            status=verification.status, requestee=verification.requestee, created_at=verification.created_at,
            updated_at=verification.updated_at))

    def get_verification(self, verification_id):
        try:
            verification_db = self._get_verification(verification_id)
            verification = VerificationFactory.verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.session.close()
        return verification

    def update_verification(self, verification):
        try:
            verification_db = self._get_verification(verification.id)
            verification_db.status = verification.status
            verification_db.reject_reason = verification.reject_reason
            verification_db.updated_at = datetime.utcnow()
            verification = VerificationFactory.verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.session.close()
        return verification

    def get_latest_verification_for_entity(self, entity_id):
        try:
            verification_db = self.session.query(VerificationModel).filter(VerificationModel.entity_id == entity_id)\
                .order_by(VerificationModel.created_at.desc()).first()
            if verification_db is None:
                self.session.commit()
                return None
            verification = VerificationFactory.verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        self.session.close()
        return verification

    def get_verification_list(self, verification_type, status):
        verification_query = self.session.query(VerificationModel)
        if verification_type is not None:
            verification_query = verification_query.filter(VerificationModel.verification_type == verification_type)
        if status is not None:
            verification_query = verification_query.filter(VerificationModel.status == status)
        verification_db = verification_query.all()
        verification = VerificationFactory.verification_entity_from_db_list(verification_db)
        self.session.commit()
        return verification
