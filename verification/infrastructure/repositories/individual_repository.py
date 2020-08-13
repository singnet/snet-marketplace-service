from common.logger import get_logger
from verification.domain.factory.verification_factory import VerificationFactory
from verification.infrastructure.models import IndividualVerificationModel
from verification.infrastructure.repositories.base_repository import BaseRepository

logger = get_logger(__name__)


class IndividualRepository(BaseRepository):

    def add_verification(self, verification):
        verification_db = IndividualVerificationModel(
            verification_id=verification.verification_id, username=verification.username,
            comments=verification.comment_dict_list(),
            status=verification.status, created_at=verification.created_at, updated_at=verification.updated_at)
        self.add_item(verification_db)

    def __get_verification_db(self, verification_id=None, username=None):
        verification_query = self.session.query(IndividualVerificationModel)
        if username is not None:
            verification_query = verification_query.filter(IndividualVerificationModel.username == username) \
                .order_by(IndividualVerificationModel.created_at.desc())
        elif verification_id is not None:
            verification_query = verification_query.filter(
                IndividualVerificationModel.verification_id == verification_id)
        else:
            return None
        verification_db = verification_query.first()
        return verification_db

    def get_verification(self, verification_id=None, username=None):
        try:
            verification_db = self.__get_verification_db(verification_id=verification_id, username=username)
            verification = None
            if verification_db is not None:
                verification = VerificationFactory.individual_verification_entity_from_db(verification_db)
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return verification

    def update_verification(self, verification):
        try:
            verification_db = self.__get_verification_db(verification_id=verification.verification_id)
            if verification_db is None:
                logger.error(f"Verification not found with id {verification.verification_id}")
                raise Exception("verification not found")
            verification_db.status = verification.status
            verification_db.updated_at = verification.updated_at,
            verification_db.comments = verification.comment_dict_list()
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def get_verification_with_status(self, status, limit):
        try:
            verification_db = self.session.query(IndividualVerificationModel) \
                .filter(IndividualVerificationModel.status == status).limit(limit).all()
            verification = VerificationFactory.individual_verification_entity_list_from_db(verification_db)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return verification
