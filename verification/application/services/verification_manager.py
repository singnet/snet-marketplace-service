import json
from datetime import datetime
from uuid import uuid4

from common import boto_utils
from common.exceptions import MethodNotImplemented
from common.logger import get_logger
from verification.config import REGION_NAME, REGISTRY_ARN, \
    VERIFIED_MAIL_DOMAIN
from verification.constants import VerificationType, VerificationStatus, IndividualVerificationStatus
from verification.domain.models.duns_verification import DUNSVerification
from verification.domain.models.individual_verification import IndividualVerification
from verification.domain.models.verfication import Verification
from verification.exceptions import NotAllowedToInitiateException, BadRequestException
from verification.infrastructure.repositories.duns_repository import DUNSRepository
from verification.infrastructure.repositories.individual_repository import IndividualRepository
from verification.infrastructure.repositories.verification_repository import VerificationRepository

verification_repository = VerificationRepository()
duns_repository = DUNSRepository()
individual_repository = IndividualRepository()
logger = get_logger(__name__)


class VerificationManager:

    def __init__(self):
        self.boto_utils = boto_utils.BotoUtils(region_name=REGION_NAME)

    def initiate_verification(self, verification_details, username):
        verification_type = verification_details["type"]
        verification_id = uuid4().hex
        current_time = datetime.utcnow()
        logger.info(f"initiate verification for type: {verification_type}")
        if verification_type == VerificationType.INDIVIDUAL.value:
            entity_id = username
            verification = Verification(verification_id, verification_type, entity_id,
                                        VerificationStatus.PENDING.value, username, current_time, current_time)
            self.initiate_individual_verification(verification)

        elif verification_type == VerificationType.DUNS.value:
            entity_id = verification_details["entity_id"]
            logger.info(f"initiate verification for type: {verification_type} entity_id: {entity_id}")
            verification = Verification(verification_id, verification_type, entity_id,
                                        VerificationStatus.PENDING.value, username, current_time, current_time)
            self.initiate_duns_verification(verification)
        else:
            raise MethodNotImplemented()
        return {}

    def is_allowed_bypass_verification(self, entity_id):
        if entity_id.split("@")[1] in VERIFIED_MAIL_DOMAIN:
            return True
        return False

    def __get_verification_status_for_entity(self, entity_id):
        verification = verification_repository.get_verification(entity_id=entity_id)
        if verification is None:
            return None
        return verification.status

    def initiate_individual_verification(self, verification):
        existing_status = self.__get_verification_status_for_entity(verification.entity_id)
        if existing_status == VerificationStatus.REJECTED.value:
            raise NotAllowedToInitiateException("Rejected user can not initiate verification")
        if existing_status == VerificationStatus.APPROVED.value:
            verification.status = existing_status
            self._ack_verification(verification)
            return
        individual_verification = IndividualVerification.initiate(verification.id, verification.entity_id)
        if self.is_allowed_bypass_verification(verification.entity_id):
            individual_verification.approve()
            self._ack_verification(verification)
        individual_repository.add_verification(individual_verification)
        verification_repository.add_verification(verification)

    def initiate_duns_verification(self, verification):
        duns_verification = DUNSVerification(
            verification_id=verification.id, org_uuid=verification.entity_id, status=None,
            comments=[], created_at=datetime.utcnow(), updated_at=datetime.utcnow())

        duns_verification.initiate()
        verification_repository.add_verification(verification)
        duns_repository.add_verification(duns_verification)

    def callback(self, verification_details, verification_id=None, entity_id=None):
        logger.info(f"received callback for verification_id:{verification_id} with details {verification_details}")
        if entity_id is not None:
            verification = verification_repository.get_verification(entity_id=entity_id)
        elif verification_id is not None:
            verification = verification_repository.get_verification(verification_id=verification_id)
        else:
            raise BadRequestException()
        if verification is None:
            raise Exception(f"No verification found entity_id:{entity_id}, verification_id:{verification_id}")
        if verification.type == VerificationType.INDIVIDUAL.value:
            current_verification_repo = individual_repository
        elif verification.type == VerificationType.DUNS.value:
            current_verification_repo = duns_repository
        else:
            raise MethodNotImplemented()

        if verification.status != VerificationStatus.APPROVED.value:
            current_verification = current_verification_repo.get_verification(verification.id)
            if current_verification is None:
                raise Exception(f"Verification not found with {verification_id} {entity_id}")
            current_verification.update_callback(verification_details)
            comment_list = current_verification.comment_dict_list()
            verification.reject_reason = comment_list[0]["comment"]
            verification.status = current_verification.status
            verification_repository.update_verification(verification)
            current_verification_repo.update_verification(current_verification)
            self._ack_verification(verification)
        else:
            raise MethodNotImplemented()
        return {}

    def _ack_verification(self, verification):
        VERIFICATION_SERVICE = "VERIFICATION_SERVICE"
        verification_status = verification.status

        if verification_status in [VerificationStatus.ERROR.value, VerificationStatus.FAILED.value]:
            verification_status = VerificationStatus.REJECTED.value

        if verification.type == VerificationType.INDIVIDUAL.value:
            payload = {
                "path": "/org/verification",
                "queryStringParameters": {
                    "status": verification_status,
                    "username": verification.entity_id,
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
        verification = verification_repository.get_verification(entity_id=entity_id)
        if verification is None:
            return {}
        response = verification.to_response()
        if verification.type == VerificationType.INDIVIDUAL.value:
            jumio_verification = individual_repository.get_verification(verification.id)
            response["individual"] = jumio_verification.to_dict()
        elif verification.type == VerificationType.DUNS.value:
            duns_verification = duns_repository.get_verification(org_uuid=entity_id)
            response["duns"] = duns_verification.to_dict()
        return response

    def get_verifications(self, parameters):
        status = parameters.get("status", None)
        verification_type = parameters.get("type", None)
        verification_list = verification_repository.get_verification_list(verification_type, status)
        response = [verification.to_response() for verification in verification_list]
        if verification_type == VerificationType.INDIVIDUAL.value:
            for verification in response:
                individual_verification = individual_repository.get_verification(verification_id=verification["id"])
                verification["individual"] = individual_verification.to_dict()
        if verification_type == VerificationType.DUNS.value:
            for verification in response:
                dun_verification = duns_repository.get_verification(verification["id"])
                verification["duns"] = dun_verification.to_dict()
        return response

    def get_pending_individual_verification(self, limit):
        verification_list = individual_repository.get_verification_with_status(IndividualVerificationStatus.PENDING, limit)
        return [verification.to_dict() for verification in verification_list]
