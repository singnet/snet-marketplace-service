from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from verification.config import NETWORKS, NETWORK_ID
from verification.infrastructure.models import UserVerificationModel
from verification.constants import UserVerificationStatus

engine = create_engine(
    f"{NETWORKS[NETWORK_ID]['db']['DB_DRIVER']}://{NETWORKS[NETWORK_ID]['db']['DB_USER']}:"
    f"{NETWORKS[NETWORK_ID]['db']['DB_PASSWORD']}"
    f"@{NETWORKS[NETWORK_ID]['db']['DB_HOST']}:"
    f"{NETWORKS[NETWORK_ID]['db']['DB_PORT']}/{NETWORKS[NETWORK_ID]['db']['DB_NAME']}", echo=False)

Session = sessionmaker(bind=engine)
default_session = Session()


class UserVerificationRepository:
    def __init__(self):
        self.session = default_session

    def add_transaction(self, transaction_id, user_reference_id):
        try:
            self.session.add(UserVerificationModel(transaction_id=transaction_id, user_reference_id=user_reference_id,
                                                   verification_status=UserVerificationStatus.PENDING))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def update_jumio_reference(self, transaction_id, jumio_reference, error_code, verification_status):
        try:
            user_verification_item = self.session.query(UserVerificationModel) \
                .filter(UserVerificationModel.transaction_id == transaction_id) \
                .first()
            user_verification_item.jumio_reference = jumio_reference
            user_verification_item.verification_status = verification_status
            if error_code:
                user_verification_item.error_code = error_code
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def complete_transaction(self, verification_response):
        try:
            user_verification_item = self.session.query(UserVerificationModel) \
                .filter(UserVerificationModel.jumio_reference == verification_response.jumioIdScanReference) \
                .first()
            user_verification_item.call_back_type = verification_response.callBackType
            user_verification_item.verification_status = verification_response.verificationStatus
            user_verification_item.id_scan_status = verification_response.idScanStatus
            user_verification_item.id_scan_source = verification_response.idScanSource
            user_verification_item.transaction_date = verification_response.transactionDate
            user_verification_item.callback_date = verification_response.callbackDate
            user_verification_item.identity_verification = verification_response.identityVerification
            user_verification_item.id_type = verification_response.idType

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_status(self, user_reference_id):
        try:
            user_verification_item = self.session.query(UserVerificationModel) \
                .filter(UserVerificationModel.user_reference_id == user_reference_id) \
                .first()
            status = user_verification_item.verification_status
            return status
        except Exception as e:
            self.session.rollback()
            raise e
