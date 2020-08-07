from datetime import datetime

from common.logger import get_logger
from verification.domain.factory.verification_factory import VerificationFactory
from verification.infrastructure.models import VerificationModel
from verification.infrastructure.repositories.base_repository import BaseRepository

logger = get_logger(__name__)


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
        return verifications

    def __get_verification(self, verification_id=None, entity_id=None):
        verification_db_query = self.session.query(VerificationModel)
        if entity_id is not None:
            verification_db_query = verification_db_query.filter(VerificationModel.entity_id == entity_id)\
                .order_by(VerificationModel.created_at.desc())
        elif verification_id is not None:
            verification_db_query = verification_db_query.filter(VerificationModel.id == verification_id)
        else:
            return None
        verification_db = verification_db_query.first()
        return verification_db

    def add_verification(self, verification):
        self.add_item(VerificationModel(
            id=verification.id, verification_type=verification.type, entity_id=verification.entity_id,
            status=verification.status, requestee=verification.requestee, created_at=verification.created_at,
            updated_at=verification.updated_at))

    def get_verification(self, verification_id=None, entity_id=None):
        try:
            verification_db = self.__get_verification(verification_id, entity_id)
            verification = None
            if verification_db is not None:
                verification = VerificationFactory.verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return verification

    def update_verification(self, verification):
        try:
            verification_db = self.__get_verification(verification_id=verification.id)
            if verification_db is None:
                logger.error(f"Verification not found with id {verification.verification_id}")
                raise Exception(f"No verification found for {verification.id}")
            verification_db.status = verification.status
            verification_db.reject_reason = verification.reject_reason
            verification_db.updated_at = datetime.utcnow()
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def get_verification_list(self, verification_type, status):
        try:
            verification_query = self.session.query(VerificationModel)
            if verification_type is not None:
                verification_query = verification_query.filter(VerificationModel.verification_type == verification_type)
            if status is not None:
                verification_query = verification_query.filter(VerificationModel.status == status)
            verification_db = verification_query.all()
            verification = VerificationFactory.verification_entity_from_db_list(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return verification
