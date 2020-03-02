from registry.infrastructure.repositories.base_repository import BaseRepository
from verification.domain.factory.verification_factory import VerificationFactory
from verification.infrastructure.models import VerificationModel


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

    def add_verification(self, verification):
        self.add_item(VerificationModel(
            id=verification.id, verification_type=verification.type, entity_id=verification.entity_id,
            status=verification.status, requestee=verification.requestee, created_at=verification.created_at,
            updated_at=verification.updated_at))
