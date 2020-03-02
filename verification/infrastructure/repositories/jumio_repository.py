from verification.infrastructure.models import JumioVerificationModel
from verification.infrastructure.repositories.base_repository import BaseRepository


class JumioRepository(BaseRepository):

    def add_jumio_verification(self, verification):
        self.add_item(JumioVerificationModel(
            verification_id=verification.verification_id, username=verification.username,
            jumio_reference_id=verification.jumio_reference_id, verification_status=verification.verification_status,
            redirect_url=verification.redirect_url
        ))
