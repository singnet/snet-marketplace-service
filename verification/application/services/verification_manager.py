import json
from datetime import datetime
from uuid import uuid4

from common import boto_utils
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from verification.config import ALLOWED_VERIFICATION_REQUESTS, DAPP_POST_JUMIO_URL, REGION_NAME, REGISTRY_ARN, \
    VERIFIED_MAIL_DOMAIN
from verification.constants import VerificationType, VerificationStatus, JumioTransactionStatus, \
    REJECTED_JUMIO_VERIFICATION, FAILED_JUMIO_VERIFICATION, VERIFIED_JUMIO_VERIFICATION
from verification.domain.models.duns_verification import DUNSVerification
from verification.domain.models.verfication import Verification
from verification.domain.services.jumio_service import JumioService
from verification.exceptions import NotAllowedToInitiateException
from verification.infrastructure.repositories.duns_repository import DUNSRepository
from verification.infrastructure.repositories.jumio_repository import JumioRepository
from verification.infrastructure.repositories.verification_repository import VerificationRepository

verification_repository = VerificationRepository()
jumio_repository = JumioRepository()
duns_repository = DUNSRepository()

logger = get_logger(__name__)


class VerificationManager:

    def __init__(self):
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
            if self.is_allowed_bypass_verification(entity_id):
                return self.initiate_snet_verification(verification)
            self.terminate_if_not_allowed_to_verify(entity_id, verification_type)
            return self.initiate_jumio_verification(username, verification)
        elif verification_type == VerificationType.DUNS.value:
            entity_id = verification_details["entity_id"]
            logger.info(f"initiate verification for type: {verification_type} entity_id: {entity_id}")
            verification = Verification(verification_id, verification_type, entity_id,
                                        VerificationStatus.PENDING.value, username, current_time, current_time)
            self.initiate_duns_verification(verification)
            return {}
        else:
            raise MethodNotImplemented()

    def is_allowed_bypass_verification(self, entity_id):
        if entity_id.split("@")[1] in VERIFIED_MAIL_DOMAIN:
            return True
        return False

    def initiate_snet_verification(self, verification):
        verification.status = VerificationStatus.APPROVED.value
        verification_repository.add_verification(verification)
        self._ack_verification(verification)
        return {
            "redirect_url": ""
        }

    def initiate_jumio_verification(self, username, verification):
        jumio_verification = JumioService(jumio_repository).initiate(username, verification.id)
        verification_repository.add_verification(verification)
        jumio_repository.add_jumio_verification(jumio_verification)
        return {
            "redirect_url": jumio_verification.redirect_url
        }

    def initiate_duns_verification(self, verification):
        duns_verification = DUNSVerification(
            verification_id=verification.id, org_uuid=verification.entity_id, status=None,
            comments=[], created_at=datetime.utcnow(), update_at=datetime.utcnow())

        duns_verification.initiate()
        verification_repository.add_verification(verification)
        duns_repository.add_verification(duns_verification)

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
                verification.status = VerificationStatus.ERROR.value
                verification_repository.update_verification(verification)
        else:
            raise MethodNotImplemented()
        return DAPP_POST_JUMIO_URL

    def callback(self, verification_id, verification_details):
        logger.info(f"received callback for verification_id:{verification_id} with details {verification_details}")
        verification = verification_repository.get_verification(verification_id)

        if verification.type == VerificationType.JUMIO.value:
            jumio_verification = JumioService(jumio_repository).callback(verification_id, verification_details)

            if jumio_verification.verification_status in REJECTED_JUMIO_VERIFICATION:
                verification.status = VerificationStatus.REJECTED.value
            elif jumio_verification.verification_status in FAILED_JUMIO_VERIFICATION:
                verification.status = VerificationStatus.FAILED.value
            elif jumio_verification.verification_status in VERIFIED_JUMIO_VERIFICATION:
                verification.status = VerificationStatus.APPROVED.value
            else:
                raise MethodNotImplemented()
            verification.reject_reason = jumio_verification.construct_reject_reason()
            verification_repository.update_verification(verification)

        elif verification.type == VerificationType.DUNS.value:
            duns_verification = duns_repository.get_verification(verification_id)
            duns_verification.update_callback(verification_details)
            comment_list = duns_verification.comment_dict_list()
            verification.reject_reason = comment_list[0]["comment"]
            verification.status = duns_verification.status
            verification_repository.update_verification(verification)
            duns_repository.update_verification(duns_verification)
        else:
            raise MethodNotImplemented()
        self._ack_verification(verification)
        return {}

    def slack_callback(self, entity_id, verification_details):
        verification = verification_repository.get_latest_verification_for_entity(entity_id)
        if verification.type == VerificationType.DUNS.value:
            duns_verification = duns_repository.get_verification(verification.id)
            duns_verification.update_callback(verification_details)
            comment_list = duns_verification.comment_dict_list()
            verification.reject_reason = comment_list[0]["comment"]
            verification.status = duns_verification.status
            verification_repository.update_verification(verification)
            duns_repository.update_verification(duns_verification)
        else:
            raise MethodNotImplemented()
        self._ack_verification(verification)
        return {}

    def _ack_verification(self, verification):
        VERIFICATION_SERVICE = "VERIFICATION_SERVICE"
        verification_status = verification.status

        if verification_status in [VerificationStatus.ERROR.value, VerificationStatus.FAILED.value]:
            verification_status = VerificationStatus.REJECTED.value

        if verification.type == VerificationType.JUMIO.value:
            payload = {
                "path": "/org/verification",
                "queryStringParameters": {
                    "status": verification_status,
                    "username": verification.entity_id,
                    "verification_type": verification.type,
                    "updated_by": VERIFICATION_SERVICE
                }
            }
            lambda_response = self.boto_utils.invoke_lambda(REGISTRY_ARN["ORG_VERIFICATION"],
                                                            invocation_type="RequestResponse",
                                                            payload=json.dumps(payload))

            if lambda_response["statusCode"] != 201:
                raise Exception(f"Failed to acknowledge callback to registry")
        elif verification.type == VerificationType.DUNS.value:
            payload = {
                "path": "/org/verification",
                "queryStringParameters": {
                    "status": verification_status,
                    "org_uuid": verification.entity_id,
                    "verification_type": verification.type,
                    "comment": verification.reject_reason,
                    "updated_by": VERIFICATION_SERVICE
                }
            }
            lambda_response = self.boto_utils.invoke_lambda(REGISTRY_ARN["ORG_VERIFICATION"],
                                                            invocation_type="RequestResponse",
                                                            payload=json.dumps(payload))

            if lambda_response["statusCode"] != 201:
                raise Exception(f"Failed to acknowledge callback to registry")
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
        elif verification.type == VerificationType.DUNS.value:
            duns_verification = duns_repository.get_verification(org_uuid=entity_id)
            response["duns"] = duns_verification.to_dict()
        return response

    def get_verifications(self, parameters):
        status = parameters.get("status", None)
        verification_type = parameters.get("type", None)
        verification_list = verification_repository.get_verification_list(verification_type, status)
        response = [verification.to_response() for verification in verification_list]
        if verification_type == VerificationType.DUNS.value:
            for verification in response:
                dun_verification = duns_repository.get_verification(verification["id"])
                verification["duns"] = dun_verification.to_dict()
        return response
