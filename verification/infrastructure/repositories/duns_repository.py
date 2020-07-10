from common.logger import get_logger
from verification.domain.factory.verification_factory import VerificationFactory
from verification.infrastructure.models import DUNSVerificationModel
from verification.infrastructure.repositories.base_repository import BaseRepository

logger = get_logger(__name__)


class DUNSRepository(BaseRepository):

    def add_verification(self, verification):
        verification_db = DUNSVerificationModel(
            verification_id=verification.verification_id, org_uuid=verification.org_uuid,
            comments=verification.comment_dict_list(),
            status=verification.status, created_at=verification.created_at, updated_at=verification.updated_at)
        self.add_item(verification_db)

    def _get_verification(self, verification_id=None, org_uuid=None):
        verification_query = self.session.query(DUNSVerificationModel)
        if org_uuid is not None:
            verification_query = verification_query.filter(DUNSVerificationModel.org_uuid == org_uuid) \
                .order_by(DUNSVerificationModel.created_at.desc())
        elif verification_id is not None:
            verification_query = verification_query.filter(DUNSVerificationModel.verification_id == verification_id)
        verification_db = verification_query.first()
        return verification_db

    def get_verification(self, verification_id=None, org_uuid=None):
        verification_db = self._get_verification(verification_id=verification_id, org_uuid=org_uuid)
        if verification_db is None:
            return None
        verification = VerificationFactory.duns_verification_entity_from_db(verification_db)
        self.session.commit()
        return verification

    def update_verification(self, verification):
        verification_db = self._get_verification(verification_id=verification.verification_id)
        if verification_db is None:
            logger.error(f"Verification not found with id {verification.verification_id}")
            raise Exception("verification not found")
        verification_db.status = verification.status
        verification_db.updated_at = verification.updated_at,
        verification_db.comments = verification.comment_dict_list()
        self.session.commit()
