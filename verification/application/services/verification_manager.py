from datetime import datetime
from uuid import uuid4

from common.exceptions import MethodNotImplemented
from verification.config import ALLOWED_VERIFICATION_REQUESTS
from verification.constants import VerificationType, VerificationStatus
from verification.domain.models.verfication import Verification
from verification.domain.services.jumio_service import JumioService
from verification.exceptions import NotAllowedToInitiate
from verification.infrastructure.repositories.jumio_repository import JumioRepository
from verification.infrastructure.repositories.verification_repository import VerificationRepository

verification_repository = VerificationRepository()
jumio_repository = JumioRepository()


class VerificationManager:

    def initiate_verification(self, verification_details, username):
        verification_type = verification_details["type"]
        entity_id = verification_details["entity_id"]
        verification_id = uuid4().hex
        current_time = datetime.utcnow()
        verification = Verification(verification_id, verification_type, entity_id,
                                    VerificationStatus.PENDING.value, username, current_time, current_time)
        if verification_type == VerificationType.JUMIO.value:
            self.terminate_if_not_allowed_to_verify(entity_id, verification_type)
            return self.initiate_jumio_verification(username, verification)
        else:
            raise MethodNotImplemented()

    def initiate_jumio_verification(self, username, verification):
        jumio_verification = JumioService().initiate(username, verification.id)
        verification_repository.add_verification(verification)
        jumio_repository.add_jumio_verification(jumio_verification)
        return {
            "redirect_url": jumio_verification.redirect_url
        }

    def terminate_if_not_allowed_to_verify(self, entity_id, verification_type):
        verifications = verification_repository.get_all_verification(entity_id, verification_type)
        if len(verifications) > ALLOWED_VERIFICATION_REQUESTS:
            raise NotAllowedToInitiate(f"Exceeded max({ALLOWED_VERIFICATION_REQUESTS}) requests")

    def submit(self):
        pass

    def call_back(self):
        pass
