from enum import Enum


class JumioVerificationStatus(Enum):
    PENDING = "PENDING"
    SUBMIT_SUCCESS = "SUBMIT_SUCCESS"
    ERROR = "ERROR"
    APPROVED_VERIFIED = "APPROVED_VERIFIED"
    DENIED_FRAUD = "DENIED_FRAUD"
    DENIED_UNSUPPORTED_ID_TYPE = "DENIED_UNSUPPORTED_ID_TYPE"
    DENIED_UNSUPPORTED_ID_COUNTRY = "DENIED_UNSUPPORTED_ID_COUNTRY"
    ERROR_NOT_READABLE_ID = "ERROR_NOT_READABLE_ID"
    NO_ID_UPLOADED = "NO_ID_UPLOADED"


REJECTED_JUMIO_VERIFICATION = [
    JumioVerificationStatus.DENIED_FRAUD.value, JumioVerificationStatus.DENIED_UNSUPPORTED_ID_TYPE.value,
    JumioVerificationStatus.DENIED_UNSUPPORTED_ID_COUNTRY.value
]

FAILED_JUMIO_VERIFICATION = [
    JumioVerificationStatus.ERROR_NOT_READABLE_ID.value, JumioVerificationStatus.NO_ID_UPLOADED.value
]

VERIFIED_JUMIO_VERIFICATION = [
    JumioVerificationStatus.APPROVED_VERIFIED.value
]


class VerificationStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class VerificationType(Enum):
    JUMIO = "JUMIO"
    DUNS = "DUNS"


class JumioTransactionStatus(Enum):
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    DONE = "DONE"
    ERROR = "ERROR"
