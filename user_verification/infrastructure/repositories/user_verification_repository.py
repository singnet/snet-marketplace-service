from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from user_verification.config import NETWORKS, NETWORK_ID
from user_verification.infrastructure.models import UserVerificationModel

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

    def add_verification_response(self, verification_response):
        try:
            self.session.add(UserVerificationModel(
                call_back_type=verification_response.callBackType,
                jumio_id_scan_reference=verification_response.jumioIdScanReference,
                verification_status=verification_response.verificationStatus,
                id_scan_status=verification_response.idScanStatus,
                id_scan_source=verification_response.idScanSource,
                transaction_date=verification_response.transactionDate,
                callback_date=verification_response.callbackDate,
                identity_verification=verification_response.identityVerification,
                id_type=verification_response.idType
            ))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
