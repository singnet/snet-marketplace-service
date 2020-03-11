from datetime import datetime
from uuid import uuid4

from common import boto_utils
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from verification.config import ALLOWED_VERIFICATION_REQUESTS, DAPP_POST_JUMIO_URL, REGION_NAME, REGISTRY_ARN
from verification.constants import VerificationType, VerificationStatus, JumioTransactionStatus, \
    REJECTED_JUMIO_VERIFICATION, FAILED_JUMIO_VERIFICATION, VERIFIED_JUMIO_VERIFICATION
from verification.domain.models.verfication import Verification
from verification.domain.services.jumio_service import JumioService
from verification.exceptions import NotAllowedToInitiateException
from verification.infrastructure.repositories.jumio_repository import JumioRepository
from verification.infrastructure.repositories.verification_repository import VerificationRepository

verification_repository = VerificationRepository()
jumio_repository = JumioRepository()

logger = get_logger(__name__)


class VerificationManager:

    def __index__(self):
        self.boto_utils = boto_utils.BotoUtils(region_name=REGION_NAME)

    def initiate_verification(self, verification_details, username):
        verification_type = verification_details["type"]
        verification_id = uuid4().hex
        current_time = datetime.utcnow()
        logger.info(f"initiate verification for type: {verification_type}")
        if verification_type == VerificationType.JUMIO.value:
            entity_id = username
            logger.info(f"initiate verification for type: {verification_type} entity_id: {entity_id}")
            verification = Verification(verification_id, verification_type, entity_id,
                                        VerificationStatus.PENDING.value, username, current_time, current_time)

            self.terminate_if_not_allowed_to_verify(entity_id, verification_type)
            return self.initiate_jumio_verification(username, verification)
        else:
            raise MethodNotImplemented()

    def initiate_jumio_verification(self, username, verification):
        jumio_verification = JumioService(jumio_repository).initiate(username, verification.id)
        verification_repository.add_verification(verification)
        jumio_repository.add_jumio_verification(jumio_verification)
        return {
            "redirect_url": jumio_verification.redirect_url
        }

    def terminate_if_not_allowed_to_verify(self, entity_id, verification_type):
        verifications = verification_repository.get_all_verification(entity_id, verification_type)

        if len(verifications) >= ALLOWED_VERIFICATION_REQUESTS:
            raise NotAllowedToInitiateException(f"Exceeded max({ALLOWED_VERIFICATION_REQUESTS}) requests")

    def submit(self, verification_id, transaction_status):
        logger.info(f"submit from jumio for verification_id: {verification_id} "
                    f"with transaction_status: {transaction_status}")
        verification = verification_repository.get_verification(verification_id)
        if verification.type == VerificationType.JUMIO.value:
            jumio_verification = JumioService(jumio_repository).submit(verification.id, transaction_status)

            if jumio_verification.transaction_status == JumioTransactionStatus.ERROR.value:
                verification_status = VerificationStatus.ERROR.value
                verification_repository.update_status(verification.id, verification_status)
        else:
            raise MethodNotImplemented()
        return DAPP_POST_JUMIO_URL

    def callback(self, verification_id, verification_details):
        logger.info(f"received callback for verification_id:{verification_id} with details {verification_details}")
        verification = verification_repository.get_verification(verification_id)
        if verification.type == VerificationType.JUMIO.value:
            jumio_verification = JumioService(jumio_repository).callback(verification_id, verification_details)

            if jumio_verification.verification_status in REJECTED_JUMIO_VERIFICATION:
                verification_status = VerificationStatus.REJECTED.value
            elif jumio_verification.verification_status in FAILED_JUMIO_VERIFICATION:
                verification_status = VerificationStatus.FAILED.value
            elif jumio_verification.verification_status in VERIFIED_JUMIO_VERIFICATION:
                verification_status = VerificationStatus.APPROVED.value
            else:
                raise MethodNotImplemented()
            verification_repository.update_status(verification_id, verification_status)
        else:
            raise MethodNotImplemented()
        return {}

    def _ack_verification(self, verification):
        if verification.type == VerificationType.JUMIO.value:
            payload = {
                "path": "/org/verification",
                "queryStringParameters": {
                    "status": verification.status,
                    "username": verification.entity_id,
                    "verification_type": verification.type
                }
            }
            self.boto_utils.invoke_lambda(REGISTRY_ARN["ORG_VERIFICATION"],
                                          invocation_type="RequestResponse", payload=payload)
        else:
            raise MethodNotImplemented()

    def get_status_for_entity(self, entity_id):
        verification = verification_repository.get_latest_verification_for_entity(entity_id)
        if verification is None:
            return {}
        response = verification.to_response()
        if verification.type == VerificationType.JUMIO.value:
            jumio_verification = jumio_repository.get_verification(verification.id)
            response["jumio"] = jumio_verification.to_dict()
        return response
